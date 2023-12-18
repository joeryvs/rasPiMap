jQuery(document).ready(function ($)
{
  if ($(".simple-product-price .woocommerce-Price-amount").length) 
  {
    const html = $(".woocommerce-product-details__short-description").html();
    $("input.qty").bind("change keyup input", function () {
      const pepQty = $(this).val();
      const randomName = $( ".simple-product-price .woocommerce-Price-amount").html();
      const randomName1 = randomName.split("</span>");
      const randomName2 = randomName1[1].replace(/,/g, ".");
      let pepTotalPrice = pepQty * parseFloat(randomName2);
      const pepTotalPrice1 = pepTotalPrice.toFixed(2);
      const pepTotalPrice2 = pepTotalPrice1.replace(".", ",");
      const pepTotalPriceFormatted = "<span style='font-size: 28px;'>Totaalprijs: €" + pepTotalPrice2 + "</span>";
      $(".woocommerce-product-details__short-description").html( html + pepTotalPriceFormatted );
    });
  } 
  else 
  {
    var html = $(".woocommerce-product-details__short-description").html();
    $("input.qty").bind("change keyup input", function () {
      var pepQty = $(this).val();
      var pepPrice = $(".woocommerce-variation-price .woocommerce-Price-amount").html();
      var pepPrice = pepPrice.split("</span>");
      var pepPrice = pepPrice[1].replace(/,/g, ".");
      let pepTotalPrice = pepQty * parseFloat(pepPrice);
      var pepTotalPrice1 = pepTotalPrice.toFixed(2);
      var pepTotalPrice2 = pepTotalPrice1.replace(".", ",");
      var pepTotalPriceFormatted = "<span style='font-size: 28px;'>Totaalprijs: €" + pepTotalPrice2 + "</span>";
      $(".woocommerce-product-details__short-description").html(html + pepTotalPriceFormatted);
    });
  }
});