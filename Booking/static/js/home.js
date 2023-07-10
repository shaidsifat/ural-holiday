let placeInput = null;
let multiDepartureAt, multiArrivalAt;


document.getElementById('book_btn').click();

function uralBooking(cityName) {

  let tabContents, tabLinks;

  tabContents = document.getElementsByClassName('tabcontent');
  for (let tabContent of tabContents) {
    tabContent.style.display = 'none';
  }

  tabLinks = document.getElementsByClassName('tablinks');
  for (let tabLink of tabLinks) {
    tabLink.className = tabLink.className.replaceAll(' active', '');
  }

  document.getElementById(cityName).style.display = 'block';

  switch (cityName) {
    case 'Book':
      document.getElementById('book_btn').className += ' active';
      break;
    case 'Trips':
      document.getElementById('my_trips_btn').className += ' active';
      break;
    case 'Flight':
      document.getElementById('flight_status_btn').className += ' active';
      break;
  }
}

  //hide search modal in mobile view on close
  
  function closeSearchModel(){
    $(".flight-search-panel").hide()
    $('#mobileView_deparuter_at_input').show();
    $('#mobileView_arrival_at_input').show();
  }

  // passenger-class panel start
  function passengerClassUpdate() {
    if (eval($('#id_adults').val()) + eval($('#id_child').val()) + eval($('#id_infant').val()) > 1)
      $('#id_passenger_class').val(eval($('#id_adults').val()) + eval($('#id_child').val()) + eval($('#id_infant').val()) + ' Passengers' + ', ' + $('[name="flight_class"]:checked').closest('label').text().trim());
    else
      $('#id_passenger_class').val(eval($('#id_adults').val()) + eval($('#id_child').val()) + eval($('#id_infant').val()) + ' Passenger' + ', ' + $('[name="flight_class"]:checked').closest('label').text().trim());
  }
  
  $('#confirm-passenger-class').click(function () {
    $(".passenger-class-panel").hide()
  });

  $('#id_passenger_class').click(function () {
    placeInput = $(this);
    let offset = $('#id_passenger_class').offset();
    $('.passenger-class-panel').css({'left': offset.left});
    $('.passenger-class-panel').show();
  });

  $("#id_adults, #id_child, #id_infant").on("input", function() {
    passengerClassUpdate();
  });

  $('#id_flight_class').change(function() {
    passengerClassUpdate();
  });
  // passenger-class panel end

  // multi passenger-class panel start
  function multiPassengerClassUpdate() {
    if (eval($('#id_multi_adults').val()) + eval($('#id_multi_child').val()) + eval($('#id_multi_infant').val()) > 1)
      $('#id_multi_passenger_class').val(eval($('#id_multi_adults').val()) + eval($('#id_multi_child').val()) + eval($('#id_multi_infant').val()) + ' Passengers' + ', ' + $('[name="multi_flight_class"]:checked').closest('label').text().trim());
    else
      $('#id_multi_passenger_class').val(eval($('#id_multi_adults').val()) + eval($('#id_multi_child').val()) + eval($('#id_multi_infant').val()) + ' Passenger' + ', ' + $('[name="multi_flight_class"]:checked').closest('label').text().trim());
  }
  
  $('#confirm-multi-passenger-class').click(function () {
    $(".passenger-class-panel").hide()
  });

  $('#id_multi_passenger_class').click(function () {
    placeInput = $(this);
    let offset = $('#id_multi_passenger_class').offset();
    $('.passenger-class-panel').css({'left': offset.left});
    $('.passenger-class-panel').show();
  });

  $("#id_multi_adults, #id_multi_child, #id_multi_infant").on("input", function() {
    multiPassengerClassUpdate();
  });

  $('#id_multi_flight_class').change(function() {
    multiPassengerClassUpdate();
  });
  // multi passenger-class panel end

//promo code logic start 
function promoDetector(){
  $("#promo_button").hide();
  $(".promo-container").show();
}
// promo  code logic end

$(document).ready(function () {
  passengerClassUpdate();

  getInitialFlights('usa');

  $('#close-notice-btn').click(function () {
    $('#notification').fadeOut('slow');
  });


  //hide return date in oneway flight

  function onewayFlightDate(){
    var conceptName = $('#id_trip_type').find(":selected").text();
    $('#id_departure_date').flatpickr({minDate: "today",dateFormat: "d M y"});
    $("input[id^='id_multi_departure_date']").flatpickr({minDate: "today",dateFormat: "d M y"});
    $("input[id^='id_multi_return_date']").flatpickr({minDate: "today",dateFormat: "d M y"});
    $('#id_return_date').flatpickr({minDate: "today",dateFormat: "d M y"});
    if (conceptName == "One Way" || conceptName == "Multi Way"){
      $(".right").hide();
      $(".md").hide();
    } else{
      $(".right").show();
      $(".md").show();
    }
  }

  onewayFlightDate();

  $('#id_trip_type').change(function() {
    onewayFlightDate();
  });
  
  $("#id_multi_trip_type").change(function() {
    onewayFlightDate();
  });


  $("#id_departure_date").on('change', function() {
    // $('#id_return_date').flatpickr().clear();
    var data = $('#id_return_date')

    data.flatpickr({minDate: new Date(this.value), dateFormat: "d M y"});
    var mydate = new Date(this.value).fp_incr(7);
    var finalDate = mydate.getDate() + " " + ["Jan", "Feb", "Mar", "Apr", "May", "Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][mydate.getMonth()] + " " + mydate.getFullYear().toString().substr(-2);
    data.val(finalDate);
    // data.set('defaultDate', this.value);
  });



  $('#id_departure_at').click(function () {
    placeInput = $(this);
    let offset = $('#id_departure_at').offset();
    $('.flight-search-panel').css({'left': offset.left, 'top': 170});
    $('.flight-search-panel').show();
    if ($('#mobileView_deparuter_at_input').is(':visible')){
      
      $('#mobileView_arrival_at_input').hide();
      $('#mobileView_deparuter_at_input').show();

    }
  });

  $('#id_arrival_at').click(function () {
    placeInput = $(this);
    let offset = $('#id_arrival_at').offset();
    $('.flight-search-panel').css({'left': offset.left, 'top': 170});
    $('.flight-search-panel').show()
    if ($('#mobileView_arrival_at_input').is(':visible')){
      $('#mobileView_deparuter_at_input').hide();
      $('#mobileView_arrival_at_input').show();
    }
  });


  // $('#id_departure_at').keyup(function () {
  //   getInitialFlights($(this).val());
  // })

  // $('#id_arrival_at').keyup(function () {
  //   getInitialFlights($(this).val());
  // })

  // $('#id_departure_at_mobileView').keyup(function () {
  //   getInitialFlights($(this).val());
  // })

  // $('#id_arrival_at_mobileView').keyup(function () {
  //   getInitialFlights($(this).val());
  // })

  $('#id_trip_type').change(function (event) {
    if (event.target.value === 'ONE_WAY' || event.target.value === 'ROUND_WAY') {
      $('.one-way-form').show();
      $('.multi-way-form').hide();
    } else {
      $('.one-way-form').hide();
      $('.multi-way-form').show();
    }
    $('#id_multi_trip_type').val(event.target.value);
  })

  $('#id_multi_trip_type').change(function (event) {
    if (event.target.value === 'ONE_WAY' || event.target.value === 'ROUND_WAY') {
      $('.one-way-form').show();
      $('.multi-way-form').hide();
    } else {
      $('.one-way-form').hide();
      $('.multi-way-form').show();
    }
    $('#id_trip_type').val(event.target.value);
  })

  $('#id_add_flight').click(function () {
    let wrapper = $('#id-field-array-wrapper');
    let length = wrapper.children().length;

    let item = `
      <div class="banner-form multi-ways-row">
        <div class="input-group select-airports">
            <a class="swap-icon"><img src="/static/images/swap-icon.png" alt=""></a>
            <input type="text" name="multi_departure_at_${length}" autocomplete="off" class="banner-input-form input-form multi_departure_at" placeholder="From" maxlength="24" required="" id="id_multi_departure_at_${length}">
            <input type="text" name="multi_arrival_at_${length}" autocomplete="off" class="banner-input-form input-to multi_arrival_at" placeholder="To" maxlength="24" required="" id="id_multi_arrival_at_${length}">
        </div>
        <div class="flex-input">
            <div class="banner-form-datepicker-area-duo w-50">
                <div class="left">
                    <span>Depart</span>
                    <input type="text" name="multi_departure_date_${length}" value="25 Aug 22" autocomplete="off" class="banner-form-datepicker-input" required="" id="id_multi_departure_date_${length}">
                </div>
            </div>
            <div class="w-50 d-flex align-items-center justify-content-center">
              <i class="fa-solid fa-xmark multi-ways-row-close"></i>
            </div>
        </div>
      </div>
    `;
    // <div class="md">-</div>
    // <div class="right">
    //     <span>Return</span>
    //     <input type="text" name="multi_return_date_${length}" value="01 Sep 22" autocomplete="off" class="banner-form-datepicker-input" id="id_multi_return_date_${length}">
    // </div>
    if (wrapper.children().length < 5) {
      wrapper.append(item);
    }
    $("input[id^='id_multi_departure_date']").flatpickr({minDate: "today",dateFormat: "d M y"});
    $("input[id^='id_multi_return_date']").flatpickr({minDate: "today",dateFormat: "d M y"});
    handleClickEvents();

    $('.multi-ways-row-close').click(function () {
      $(this).parent().parent().parent().remove();
    })
  })

  function handleClickEvents() {
    $('.multi_departure_at').on('click', function () {
      placeInput = $(this);
      let index = $('.multi_departure_at').index(this);
      $('.flight-search-panel').css({'left': $(this).first().offset().left, top: (255 + index * 85)});
      $('.flight-search-panel').show();
    });

    $('.multi_arrival_at').on('click', function () {
      placeInput = $(this);
      let index = $('.multi_arrival_at').index(this);
      $('.flight-search-panel').css({'left': $(this).first().offset().left, top: (255 + index * 85)});
      $('.flight-search-panel').show();
    });
  }

  handleClickEvents();

  // multiway view in mobile view
    $(document).on( "click","input[id^='id_multi_departure_at']", function(){
    var inputid = $(this).attr('id');
    if ($('#mobileView_deparuter_at_input').is(':visible')){
      $('#mobileView_arrival_at_input').hide();
      $('#mobileView_deparuter_at_input').show();
      var departure_mobile_id = $(".id_departure_at_mobileView")
      departure_mobile_id.attr('name', inputid);
      departure_mobile_id.attr('id', inputid);

    }
  });

  $(document).on( "click","input[id^='id_multi_arrival_at']", function(){
    var inputid = $(this).attr('id');
    if ($('#mobileView_arrival_at_input').is(':visible')){
      $('#mobileView_deparuter_at_input').hide();
      $('#mobileView_arrival_at_input').show();
      var return_mobile_id = $(".id_arrival_at_mobileView");
      return_mobile_id.attr('name', inputid);
      return_mobile_id.attr('id', inputid);
    }
  });


  var timeout = null;
  //lookup at oneway roundway deprature search 
  $(document).on( "keyup","input[id^='id_multi_departure_at']", function(){
    var searchkey = $(this).val();
      clearTimeout(timeout);

      timeout = setTimeout(function() {
        getInitialFlights(searchkey);
      }, 500);
  });
  //lookup at oneway roundway return search  id_multi_arrival_at
  $(document).on( "keyup","input[id^='id_multi_arrival_at']", function(){
    var searchkey = $(this).val();
    clearTimeout(timeout);

    timeout = setTimeout(function() {
      getInitialFlights(searchkey);
    }, 500);
});

  //lookup at oneway roundway deprature search 
 $('#id_departure_at').keyup(function() {
    var searchkey = $(this).val();
      clearTimeout(timeout);

      timeout = setTimeout(function() {
        getInitialFlights(searchkey);
      }, 500);
  });
  //lookup at oneway roundway return search 
  $('#id_arrival_at').keyup(function() {
    var searchkey = $(this).val();
    clearTimeout(timeout);

    timeout = setTimeout(function() {
      getInitialFlights(searchkey);
    }, 500);
});
  //lookup at oneway roundway deprature search  mobile view
$('.id_departure_at_mobileView').keyup(function() {
  var searchkey = $(this).val();
    clearTimeout(timeout);

    timeout = setTimeout(function() {
      getInitialFlights(searchkey);
    }, 500);
});
  //lookup at oneway roundway return search  mobile view
$('.id_arrival_at_mobileView').keyup(function() {
  var searchkey = $(this).val();
  clearTimeout(timeout);

  timeout = setTimeout(function() {
    getInitialFlights(searchkey);
  }, 500);
});

 //lookup at oneway roundway arrival at search mobile view


  $(document).click(function (e) {

    let flightSearchPanel = $('.flight-search-panel');
    let departureAt = $('#id_departure_at');
    let arrivalAt = $('#id_arrival_at');
    multiDepartureAt = $('.multi_departure_at');
    multiArrivalAt = $('.multi_arrival_at');

    if (
      !departureAt.is(e.target) && departureAt.has(e.target).length === 0 &&
      !arrivalAt.is(e.target) && arrivalAt.has(e.target).length === 0 &&
      !multiDepartureAt.is(e.target) && multiDepartureAt.has(e.target).length === 0 &&
      !multiArrivalAt.is(e.target) && multiArrivalAt.has(e.target).length === 0 &&
      !flightSearchPanel.is(e.target) && flightSearchPanel.has(e.target).length === 0
    ) {
      flightSearchPanel.hide();
    }

    let passengerclassPanel = $('.passenger-class-panel');
    let passengerClass = $('#id_passenger_class');
    let multipassengerClass = $('#id_multi_passenger_class');

    if (
      !passengerClass.is(e.target) && passengerClass.has(e.target).length === 0 &&
      !multipassengerClass.is(e.target) && multipassengerClass.has(e.target).length === 0 &&
      !passengerclassPanel.is(e.target) && passengerclassPanel.has(e.target).length === 0
    ) {
      passengerclassPanel.hide();
    }
  });

});


function getInitialFlights(value) {
  $.get(`/air/airports?term=${value}&_type=query&q=${value}`, function (data) {
    $('#flight-search').children('.flight-search-item').remove();
    data.results.forEach(item => {
      $('#flight-search').append(`<div class='flight-search-item' id='${item.id}'>${item.text}</div>`);
    })
    $('.flight-search-item').click(function (data) {
      $('.flight-search-panel').hide();
      if (placeInput) {
        placeInput.val(data.target.outerText)
      }
    });
  });
}

/*
$('.multi_departure_at').on('click', function () {
  placeInput = $(this);
  let index = $('.multi_departure_at').index(this);
  $('.flight-search-panel').css({'left': $(this).first().offset().left, top: (255 + index * 85)});
  $('.flight-search-panel').show();
});

$('.multi_arrival_at').on('click', function () {
  placeInput = $(this);
  let index = $('.multi_arrival_at').index(this);
  $('.flight-search-panel').css({'left': $(this).first().offset().left, top: (255 + index * 85)});
  $('.flight-search-panel').show();
});
*/


      jQuery( window ).scroll(function() {
    var height = jQuery(window).scrollTop();
    if(height >= 150) {
      jQuery('.header-banner-area nav.navbar').addClass('fixed-menu');
    } else {
      jQuery('.header-banner-area nav.navbar').removeClass('fixed-menu');
    }
  });