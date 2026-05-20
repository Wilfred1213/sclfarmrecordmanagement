from django.shortcuts import render, redirect, get_object_or_404
from sclApp.inventory.models import *
from django.db.models import F
from sclApp.inventory.forms import ItemForm, TransactionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone


# Create your views here.


@login_required
def inventory_dashboard(request):
    # Base Querysets needed to populate the dashboard interface
    items = Item.objects.all().order_by('category', 'name')
    categories = Category.objects.all()
    pending_returns = StoreTransaction.objects.filter(is_returnable=True, is_returned=False).select_related('item')
    returned_history = StoreTransaction.objects.filter(is_returnable=True, is_returned=True).select_related('item').order_by('-returned_at')[:20]
    low_stock = Item.objects.filter(quantity__lte=F('min_stock_level')).select_related('category')
    recent_transactions = StoreTransaction.objects.all().select_related('item', 'staff').order_by('-timestamp')[:10]

    # Initialize standard layout forms
    item_form = ItemForm()
    transaction_form = TransactionForm()

    # Track toast notification parameters for HTMX header responses
    toast_message = ""
    toast_status = "success"

    if request.method == 'POST':
        # =========================================================================
        # CASE 1: ADD NEW ITEM TO THE LIST
        # =========================================================================
        if 'submit_item' in request.POST:
            item_form = ItemForm(request.POST)
            if item_form.is_valid():
                get_item_name = item_form.cleaned_data.get('name')
                
                # Check for duplicates
                if Item.objects.filter(name__iexact=get_item_name).exists():
                    toast_message = f"Duplicate Entry: '{get_item_name}' is already listed in inventory."
                    toast_status = "error"
                    if not request.headers.get('HX-Request'):
                        messages.error(request, toast_message)
                        return redirect('inventory:inventory_dashboard')
                else:
                    item_form.save()
                    toast_message = f"Success: '{get_item_name}' has been added to the registry."
                    toast_status = "success"
                    if not request.headers.get('HX-Request'):
                        messages.success(request, toast_message)
                        return redirect('inventory:inventory_dashboard')
            else:
                toast_message = "Failed to add item. Please check form errors."
                toast_status = "error"
                if not request.headers.get('HX-Request'):
                    messages.error(request, toast_message)
                    return redirect('inventory:inventory_dashboard')

        # =========================================================================
        # CASE 2: RECORD TRANSACTION (STOCK IN / STOCK OUT)
        # =========================================================================
        elif 'submit_transaction' in request.POST:
            transaction_form = TransactionForm(request.POST)
            if transaction_form.is_valid():
                transaction = transaction_form.save(commit=False)
                item = transaction.item

                current_stock = int(item.quantity)
                requested_qty = int(transaction.quantity)

                # --- SUB-CASE A: ISSUING / COLLECTING ITEMS (OUT) ---
                if transaction.transaction_type == 'OUT':
                    if current_stock < requested_qty:
                        toast_message = f"Insufficient Stock! Available: {current_stock} {item.unit}."
                        toast_status = "error"
                        if not request.headers.get('HX-Request'):
                            messages.error(request, toast_message)
                            return redirect('inventory:inventory_dashboard')
                    else:
                        transaction.staff = request.user
                        transaction.save()
                        
                        if transaction.is_returnable:
                            toast_message = f"Issued (Returnable): {requested_qty} {item.unit} to {transaction.receiver_name}."
                            toast_status = "warning"
                        else:
                            toast_message = f"Issued (Consumable): {requested_qty} {item.unit} to {transaction.receiver_name}."
                            toast_status = "success"

                # --- SUB-CASE B: RESTOCKING / SUPPLIES (IN) ---
                elif transaction.transaction_type == 'IN':
                    transaction.staff = request.user
                    transaction.save()
                    toast_message = f"Stock Restocked: Added {requested_qty} {item.unit} to {item.name}."
                    toast_status = "success"

                if not request.headers.get('HX-Request'):
                    if toast_status == "error":
                        messages.error(request, toast_message)
                    else:
                        messages.success(request, toast_message)
                    return redirect('inventory:inventory_dashboard')
            else:
                toast_message = "Transaction rejected. Verify formatting entries."
                toast_status = "error"
                if not request.headers.get('HX-Request'):
                    messages.error(request, toast_message)
                    return redirect('inventory:inventory_dashboard')

        # ---------------------------------------------------------------------
        # THE UNIFIED HTMX INVENTORY RESPONSE INTERCEPTOR
        # ---------------------------------------------------------------------
        if request.headers.get('HX-Request'):
            # Re-fetch complete querysets from the database so values match updates instantly
            items = Item.objects.all().order_by('category', 'name')
            pending_returns = StoreTransaction.objects.filter(is_returnable=True, is_returned=False).select_related('item')
            returned_history = StoreTransaction.objects.filter(is_returnable=True, is_returned=True).select_related('item').order_by('-returned_at')[:20]
            low_stock = Item.objects.filter(quantity__lte=F('min_stock_level')).select_related('category')
            recent_transactions = StoreTransaction.objects.all().select_related('item', 'staff').order_by('-timestamp')[:10]

            context = {
                'items': items,
                'categories': categories,
                'low_stock': low_stock,
                'recent_transactions': recent_transactions,
                'item_form': ItemForm(),         # Clears form field values for next inputs
                'transaction_form': TransactionForm(), # Clears form field values for next inputs
                'pending_returns': pending_returns,
                'returned_history': returned_history,
            }
            
            response = render(request, 'inventory/dashboard.html', context)
            response['X-Toast-Message'] = toast_message
            response['X-Toast-Status'] = toast_status
            return response

    # =========================================================================
    # STANDARD GET REQUEST PIPELINE
    # =========================================================================
    context = {
        'items': items,
        'categories': categories,
        'low_stock': low_stock,
        'recent_transactions': recent_transactions,
        'item_form': item_form,
        'transaction_form': transaction_form,
        'pending_returns': pending_returns,
        'returned_history': returned_history
    }
    return render(request, 'inventory/dashboard.html', context)


def mark_as_returned(request, transaction_id):
    # 1. Fetch and process the transaction target
    transaction = get_object_or_404(StoreTransaction, id=transaction_id)
    
    toast_message = ""
    toast_status = "success"

    if request.method == 'POST':
        # Capture the input quantity from the inline form
        return_qty_input = request.POST.get('return_quantity')
        
        try:
            qty_to_return = int(return_qty_input) if return_qty_input else transaction.remaining_to_return
            
            if qty_to_return <= 0 or qty_to_return > transaction.remaining_to_return:
                toast_message = f"Invalid Quantity! Max remaining to return is {transaction.remaining_to_return}."
                toast_status = "error"
            else:
                # Update transaction metrics
                transaction.quantity_returned += qty_to_return
                
                # Check if this completely resolves the loan balance
                if transaction.quantity_returned >= transaction.quantity:
                    transaction.is_returned = True
                transaction.save()
                
                toast_message = f"Successfully returned {qty_to_return} units of {transaction.item.name}."
                toast_status = "success"
                
        except ValueError:
            toast_message = "Error: Input must be a valid whole number."
            toast_status = "error"

        # ---------------------------------------------------------------------
        # CRITICAL HTMX INTERCEPT ROUTER FOR REAL-TIME UPDATE
        # ---------------------------------------------------------------------
        if request.headers.get('HX-Request'):
            # RE-FETCH ENTIRE REGISTRY DATA SO COUNTS REDUCE INSTANTLY
            items = Item.objects.all().order_by('category', 'name')
            categories = Category.objects.all()
            pending_returns = StoreTransaction.objects.filter(is_returnable=True, is_returned=False).select_related('item')
            returned_history = StoreTransaction.objects.filter(is_returnable=True, is_returned=True).select_related('item').order_by('-returned_at')[:20]
            low_stock = Item.objects.filter(quantity__lte=F('min_stock_level'))
            recent_transactions = StoreTransaction.objects.all().select_related('item', 'staff').order_by('-timestamp')[:10]

            context = {
                'items': items,
                'categories': categories,
                'low_stock': low_stock,
                'recent_transactions': recent_transactions,
                'pending_returns': pending_returns,
                'returned_history': returned_history,
            }
            
            # Send back the full dashboard layout with custom toast response headers
            response = render(request, 'inventory/dashboard.html', context)
            response['X-Toast-Message'] = toast_message
            response['X-Toast-Status'] = toast_status
            return response

        # Standard browser fallback page reload if JavaScript is disabled
        if toast_status == "error":
            messages.error(request, toast_message)
        else:
            messages.success(request, toast_message)
        return redirect('inventory:inventory_dashboard')



@login_required
def mark_as_returned(request, transaction_id):

    transaction = get_object_or_404(StoreTransaction, id=transaction_id)

    toast_message = ""
    toast_status = "success"

    if request.method == "POST":

        return_qty_input = request.POST.get("return_quantity")

        try:
            qty_to_return = int(return_qty_input)

            # Prevent invalid values
            if qty_to_return <= 0:
                toast_message = "Return quantity must be greater than zero."
                toast_status = "error"

            elif qty_to_return > transaction.remaining_to_return:
                toast_message = (
                    f"Only {transaction.remaining_to_return} remaining to return."
                )
                toast_status = "error"

            else:

                # =========================
                # ADD STOCK BACK
                # =========================
                transaction.item.quantity += qty_to_return
                transaction.item.save()

                # =========================
                # UPDATE RETURN TRACKING
                # =========================
                transaction.quantity_returned += qty_to_return

                # Fully returned?
                if transaction.quantity_returned >= transaction.quantity:
                    transaction.is_returned = True
                    transaction.returned_at = timezone.now()

                transaction.save()

                toast_message = (
                    f"{qty_to_return} {transaction.item.unit} returned successfully."
                )
                toast_status = "success"

        except ValueError:
            toast_message = "Invalid return quantity."
            toast_status = "error"

    # =====================================
    # REFRESH LIVE DATA FOR HTMX
    # =====================================

    items = Item.objects.all().order_by("category", "name")

    pending_returns = StoreTransaction.objects.filter(
        is_returnable=True,
        is_returned=False
    ).select_related("item")

    returned_history = StoreTransaction.objects.filter(
        quantity_returned__gt=0
    ).select_related("item").order_by("-returned_at")[:20]

    low_stock = Item.objects.filter(
        quantity__lte=F("min_stock_level")
    )

    recent_transactions = StoreTransaction.objects.all().select_related(
        "item",
        "staff"
    ).order_by("-timestamp")[:10]

    context = {
        "items": items,
        "pending_returns": pending_returns,
        "returned_history": returned_history,
        "low_stock": low_stock,
        "recent_transactions": recent_transactions,
        "item_form": ItemForm(),
        "transaction_form": TransactionForm(),
    }

    # HTMX response
    if request.headers.get("HX-Request"):

        response = render(
            request,
            "inventory/dashboard.html",
            context
        )

        response["X-Toast-Message"] = toast_message
        response["X-Toast-Status"] = toast_status

        return response

    # Normal response
    if toast_status == "error":
        messages.error(request, toast_message)
    else:
        messages.success(request, toast_message)

    return redirect("inventory:inventory_dashboard")


# def mark_as_returned(request, transaction_id):
#     transaction = get_object_or_404(StoreTransaction, id=transaction_id)
    
#     toast_message = ""
#     toast_status = "success"

#     if request.method == 'POST':
#         return_qty_input = request.POST.get('return_quantity')
        
#         try:
#             qty_to_return = int(return_qty_input) if return_qty_input else transaction.remaining_to_return
            
#             if qty_to_return <= 0 or qty_to_return > transaction.remaining_to_return:
#                 toast_message = f"Invalid Quantity! Max remaining is {transaction.remaining_to_return}."
#                 toast_status = "error"
#             else:
#                 # Update loan balance metrics
#                 transaction.quantity_returned += qty_to_return
                
#                 if transaction.quantity_returned >= transaction.quantity:
#                     transaction.is_returned = True
                
#                 # Update timestamp so it moves to the top of the history list
#                 transaction.timestamp = timezone.now()
#                 transaction.save()
                
#                 toast_message = f"Successfully returned {qty_to_return} units of {transaction.item.name}."
#                 toast_status = "success"
                
#         except ValueError:
#             toast_message = "Error: Input must be a valid whole number."
#             toast_status = "error"

#         if request.headers.get('HX-Request'):
#             # Pull fresh querysets directly from the database
#             items = Item.objects.all().order_by('category', 'name')
#             categories = Category.objects.all()
            
#             pending_returns = StoreTransaction.objects.filter(
#                 is_returnable=True, 
#                 is_returned=False
#             ).select_related('item')
            
#             # Fetch anything that has had parts returned to populate the history tab
#             returned_history = StoreTransaction.objects.filter(
#                 is_returnable=True, 
#                 quantity_returned__gt=0
#             ).select_related('item').order_by('-timestamp')[:20]
            
#             low_stock = Item.objects.filter(quantity__lte=F('min_stock_level'))
#             recent_transactions = StoreTransaction.objects.all().select_related('item').order_by('-timestamp')[:10]

#             context = {
#                 'items': items,
#                 'categories': categories,
#                 'low_stock': low_stock,
#                 'recent_transactions': recent_transactions,
#                 'pending_returns': pending_returns,
#                 'returned_history': returned_history,
#             }
            
#             response = render(request, 'inventory/dashboard.html', context)
#             response['X-Toast-Message'] = toast_message
#             response['X-Toast-Status'] = toast_status
#             return response

#     if toast_status == "error":
#         messages.error(request, toast_message)
#     else:
#         messages.success(request, toast_message)
#     return redirect('inventory:inventory_dashboard')