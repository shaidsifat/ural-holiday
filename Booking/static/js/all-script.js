$("#review").owlCarousel({
    loop: true,
    margin: 30,
    responsiveClass: true,
    dots: true,
    autoplay: false,
    responsive: {
      0: {
        items: 1,
        nav: false,
      },
      600: {
        items: 2,
        nav: false,
      },
      1000: {
        items: 3,
        nav: true,
        loop: true,
      },
    },
  });
 
  $(".popular-slider").owlCarousel({
    loop: true,
    margin: 30,
    responsiveClass: true,
    dots: true,
    nav: true,
    autoplay: false,
    responsive: {
      0: {
        items: 1
      },
      600: {
        items: 2
      },
      1000: {
        items: 4
      },
    },
  });
  

     jQuery( window ).scroll(function() {
    var height = jQuery(window).scrollTop();
    if(height >= 150) {
      jQuery('.header-banner-area nav.navbar').addClass('fixed-menu');
    } else {
      jQuery('.header-banner-area nav.navbar').removeClass('fixed-menu');
    }
  });