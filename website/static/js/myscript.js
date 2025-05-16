document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
  
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });






  // cart functionality
  $(document).on('click', '.plus-cart', function () {
    let cartId = $(this).data('cart-id'); // uses data-cart-id
    let el = this.closest('.row');

    $.ajax({
        type: 'GET',
        url: '/pluscart',
        data: {
            cart_id: cartId
        },
        success: function (data) {
            $(el).find('#quantity').text(data.quantity);
            $('#amount_tt').text(data.amount);
            $('#totalamount').text(data.total);
        }
    });
});

$(document).on('click', '.minus-cart', function () {
    let cartId = $(this).data('cart-id'); // uses data-cart-id
    let el = this.closest('.row');

    $.ajax({
        type: 'GET',
        url: '/minuscart',
        data: {
            cart_id: cartId
        },
        success: function (data) {
            $(el).find('#quantity').text(data.quantity);
            $('#amount_tt').text(data.amount);
            $('#totalamount').text(data.total);
        }
    });
});
$(document).on('click', '.remove-cart', function (e) {
    e.preventDefault(); // stop href from triggering page reload

    var id = $(this).data('cart-id').toString(); // get the data-cart-id
    console.log("Sending Cart ID:", id); // check in browser console

    var to_remove = this.closest('.row'); // get the cart row to remove

    $.ajax({
        type: 'GET',
        url: '/removecart',
        data: {
            cart_id: id
        },
        success: function(data){
            console.log("Item removed. Updating totals...");
            document.getElementById('amount_tt').innerText = data.amount;
            document.getElementById('totalamount').innerText = data.total;
            to_remove.remove(); // remove item from DOM
        },
        error: function(xhr, status, error) {
            console.error("AJAX error:", error);
        }
    });
});