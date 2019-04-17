$(document).ready(function() {

    // Contact form handler
    var contactForm = $(".contact-form");
    var contactFormMethod = contactForm.attr("method");
    var contactFormEndPoint = contactForm.attr("action");

    function submitLoader(submitBtn, defaultText, doSubmit) {
      if (doSubmit) {
        submitBtn.addClass("disabled");
        submitBtn.html(`<i class="fa-spin fas fa-spinner"></i> Sending...`);
      } else {
        submitBtn.removeClass("disabled");
        submitBtn.html(defaultText);
      }
    }

    contactForm.submit(function(event) {
      event.preventDefault();
      var contactFormSubmitBtn = contactForm.find("[type='submit']");
      var contactFormSubmitBtnTxt = contactFormSubmitBtn.text();
      var contactFormData = contactForm.serialize();
      var thisForm = $(this);
      submitLoader(contactFormSubmitBtn, "", true);
      $.ajax({
        url: contactFormEndPoint,
        method: contactFormMethod,
        data: contactFormData,
        success: function(data) {
          contactForm[0].reset();
          $.alert({
            title: "Success!",
            content: data.message,
            theme: "modern"
          });
          setTimeout(function() {
            submitLoader(contactFormSubmitBtn, contactFormSubmitBtnTxt, false);
          }, 500);
        },
        error: function(error) {
          var errorData = error.responseJSON;
          var error_messages = "";
          $.each(errorData, function(key, value) {
            error_messages += `<b>${key}:</b> ${value[0].message}<br>`;
          });
          $.alert({
            title: "Sorry!",
            content: error_messages,
            theme: "modern"
          });
          console.log("error");
          setTimeout(function() {
            submitLoader(contactFormSubmitBtn, contactFormSubmitBtnTxt, false);
          }, 500);
        },
      });
    });

    // Auto Search
    var searchForm = $(".search-form");
    var searchInput = searchForm.find("[name='q']");
    var searchBtn = searchForm.find("[type='submit']");
    var typingTimer;
    var typingInterval = 500;

    searchInput.keyup(function(event) {
      clearTimeout(typingTimer);
      typingTimer = setTimeout(performSearch, typingInterval);
    });
    searchInput.keydown(function(event) {
      clearTimeout(typingTimer);
    });

    function searchLoader() {
      searchBtn.addClass("disabled");
      searchBtn.html(`<i class="fa-spin fas fa-spinner"></i> Searching...`);
    }

    function performSearch() {
      searchLoader();
      var query = searchInput.val();
      setTimeout(function() {
        window.location.href = "/search/?q=" + query;
      }, 1000);
    }

    // Cart add products
    var productForm = $(".form-product-ajax");
    productForm.submit(function(event) {
      event.preventDefault();
      var thisForm = $(this);
      // var actionEndpoint = thisForm.attr("action");
      var actionEndpoint = thisForm.attr("data-endpoint");
      var httpMethod = thisForm.attr("method");
      var formData = thisForm.serialize();

      $.ajax({
        url: actionEndpoint,
        method: httpMethod,
        data: formData,
        success: function(data) {
          var submitSpan = thisForm.find(".submit-span")
          if (data.added) {
            submitSpan.html(`In Cart <button type="submit" class="btn btn-danger my-3">Remove</button>`);
          } else {
            submitSpan.html(`<button type="submit" class="btn btn-success my-3">Add to Cart</button>`);
          }
          var navbarCount = $(".navbar-cart-count");
          navbarCount.text (data.cartItemCount)
          var currentPath = window.location.href;
          if (currentPath.indexOf("cart") !== -1) {
            refreshCart();
          }
        },
        error: function(errorData) {
          $.alert({
            title: "Oops!",
            content: "An error occurred",
            theme: "modern"
          });
          console.log("error");
        }
      });
    });

    function refreshCart() {
      var currentUrl = window.location.href;
      var cartTable = $(".cart-table");
      var cartBody = cartTable.find(".cart-body");
      var productRows = cartBody.find(".cart-products");

      var refreshCartUrl = "/api/cart/";
      var refreshCartMethod = "GET";
      var data = {};
      $.ajax({
        url: refreshCartUrl,
        method: refreshCartMethod,
        data: data,
        success: function(data) {
          console.log("success");
          var hiddenCartItemRemoveForm = $(".cart-item-remove-form");
          if (data.products.length > 0) {
            productRows.html("")
            var i = data.products.length
            $.each(data.products, function(index, element) {
              var newCartItemRemove = hiddenCartItemRemoveForm.clone();
              newCartItemRemove.css("display", "block"); // newCartItemRemove.removeClass("hidden-class")
              newCartItemRemove.find(".cart-item-product-id").val(element.id);
              cartBody.prepend(`
              <tr>
                <th scope="row">${i}</th>
                <td><a href="${element.url}">${element.name}</a>${newCartItemRemove.html()}</td>
                <td>${element.price}</td>
              </tr>
              `);
              i--;
            });
            cartBody.find(".cart-subtotal").text(data.subtotal);
            cartBody.find(".cart-total").text(data.total);
          } else {
            window.location.href = currentUrl;
          }
        },
        error: function(errorData) {
          $.alert({
            title: "Oops!",
            content: "An error occurred",
            theme: "modern"
          });
          console.log("error");
        }
      });
    }
});