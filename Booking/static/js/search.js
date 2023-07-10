import { format } from "https://esm.run/date-fns";

(function ($) {
  "use strict";

  $(document).ready(function () {
    search.init();
    search.setInitialDepartDate();
  });

  var search = {
    setInitialDepartDate: function () {
      const formattedDate = format(new Date(), "dd MMM yy");
      $("input[name=departure_date]").val(formattedDate);
    },

    init: function () {
      // LIST AND GRID VIEW TOGGLE
      $(".view-type li:first-child").addClass("active");

      $(".grid-view").click(function () {
        $(".three-fourth article").attr("class", "one-third");
        $(".view-type li").removeClass("active");
        $(this).addClass("active");
      });

      $(".list-view").click(function () {
        $(".three-fourth article").attr("class", "full-width");
        $(".view-type li").removeClass("active");
        $(this).addClass("active");
      });

      $("[id^=baggage-fare-policy-]").tabs();

      $(".show-more").click(function (e) {
        $(this).siblings(".misc").toggleClass("is-misc-showing");
      });

      $("#sort-by-price").click(function () {
        $(this).addClass("is-active");
        $("#sort-by-duration").removeClass("is-active");
        $("#hidden-search-form #id_sort_by").val("price");
        $("#hidden-search-form form").submit();
      });

      $("#sort-by-duration").click(function () {
        $(this).addClass("is-active");
        $("#sort-by-price").removeClass("is-active");
        $("#hidden-search-form #id_sort_by").val("duration");
        $("#hidden-search-form form").submit();
      });

      //STAR RATING
      $("#star").raty({
        score: 3,
        path: "images/ico/",
        starOff: "star-rating-off.png",
        starOn: "star-rating-on.png",
      });
    },
  };
})(jQuery);
