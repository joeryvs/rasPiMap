jQuery(document).ready(function ($) {
  if ($(".simple-product-price .woocommerce-Price-amount").length) {
    var html = $(".woocommerce-product-details__short-description").html();
    $("input.qty").bind("change keyup input", function () {
      var pepQty = $(this).val();
      var pepPrice = $(
        ".simple-product-price .woocommerce-Price-amount"
      ).html();
      var pepPrice = pepPrice.split("</span>");
      var pepPrice = pepPrice[1].replace(/,/g, ".");
      let pepTotalPrice = pepQty * parseFloat(pepPrice);
      var pepTotalPrice1 = pepTotalPrice.toFixed(2);
      var pepTotalPrice2 = pepTotalPrice1.replace(".", ",");
      var pepTotalPriceFormatted =
        "<span style='font-size: 28px;'>Totaalprijs: €" +
        pepTotalPrice2 +
        "</span>";
      $(".woocommerce-product-details__short-description").html(
        html + pepTotalPriceFormatted
      );
    });
  } else {
    var html = $(".woocommerce-product-details__short-description").html();
    $("input.qty").bind("change keyup input", function () {
      var pepQty = $(this).val();
      var pepPrice = $(
        ".woocommerce-variation-price .woocommerce-Price-amount"
      ).html();
      var pepPrice = pepPrice.split("</span>");
      var pepPrice = pepPrice[1].replace(/,/g, ".");
      let pepTotalPrice = pepQty * parseFloat(pepPrice);
      var pepTotalPrice1 = pepTotalPrice.toFixed(2);
      var pepTotalPrice2 = pepTotalPrice1.replace(".", ",");
      var pepTotalPriceFormatted =
        "<span style='font-size: 28px;'>Totaalprijs: €" +
        pepTotalPrice2 +
        "</span>";
      $(".woocommerce-product-details__short-description").html(
        html + pepTotalPriceFormatted
      );
    });
  }
});
