$(window).on('load', function(){
    aligning()
});


$(document).ready(function(){
    niceImages()
})
function niceImages(){
  $( ".post" ).each(function() {
        id = Number($(this).attr('id'))

        length = $('#'+id+ ' .post_body img').length

        console.log(length)
        if (length == 1){
            $('#'+id+ ' .post_body .img_container').addClass('width100')
        }
        if (length == 2 || length == 4){
            $('#'+id+ ' .post_body .img_container').addClass('width50')
        }
        if (length == 3){
            $('#'+id+ ' .post_body .img_container').addClass('width50')
            $('#'+id+ ' .post_body .img_container:nth-child(3)').addClass('three_img')
            var divHeight = $('.post_images').width() / 2;
        }
    });
}
function aligning(){
    $( ".post" ).each(function() {
      id = Number($(this).attr('id'))

      length = $('#'+id+ ' .post_body img').length
      var divWidth = $('.post_images').width() / 2;
      if (length != 1){
          $( '#'+id+ " .post_body img" ).each(function() {
              //$( '#'+id+ " .post_body img" ).each(function() {
              if ($(this).height() < $(this).width()){
                  $(this).css('height', divWidth+'px');
                  $(this).css('width', 'auto');
                  $(this).parent().css('overflow', 'scroll');
                  $('#'+id+ ' .post_body img').addClass('vertical_align_bottom')
                  $('#'+id+ ' .post_body .img_container').addClass('vertical_align_bottom')
              }else{
                  // if (length == 3){
                  //     $('#'+id+ ' .post_body .img_container:nth-child(3) img').css('marginTop','-'+divWidth/2+'px');
                  //     $('#'+id+ ' .post_body .img_container:nth-child(3)').css('height', divWidth+'px');
                  // }
                  $(this).parent().css('height', divWidth+'px');
                  $(this).parent().css('overflow', 'scroll');
                  $('#'+id+ ' .post_body img').addClass('vertical_align_bottom')
                  $('#'+id+ ' .post_body .img_container').addClass('vertical_align_bottom')
              }
          });
      }
      if (length == 3){
          //third image

          $('#'+id+ ' .post_body .img_container:nth-child(3) img').css('height', 'auto');
          $('#'+id+ ' .post_body .img_container:nth-child(3) img').css('width', '100%');
          $('#'+id+ ' .post_body .img_container:nth-child(3)').css('max-height', '500px');

          //other images
          var second = $('#'+id+ ' .post_body .img_container:nth-child(2) img')
          console.log('second', 'else', second.height(), second.width())
          if (second.height() > second.width()){
              second.css('height', 'auto');
              second.css('width', '100%');
              second.parent().css('height', divWidth);
              second.parent().css('overflow', 'scroll');
              second.parent().css('padding-left', '2px', 'important');
          }else{
              second.css('height', '100%');
              second.css('width', 'auto');
              second.parent().css('height', divWidth);
              second.parent().css('overflow', 'scroll');
              second.parent().css('padding-left', '2px', 'important');
          }
          var first = $('#'+id+ ' .post_body .img_container:nth-child(1) img')
          if (first.height() > first.width()){
              first.css('height', 'auto');
              first.css('width', '100%');
              first.parent().css('height', divWidth);
              first.parent().css('overflow', 'scroll');
              first.parent().css('padding-right', '2px', 'important');
          }else{

              //first.css('display', 'none');
              first.css('height', '100%', 'important');
              first.css('width', 'auto', 'important');
              first.parent().css('height', divWidth);
              first.parent().css('overflow', 'scroll');
              first.parent().css('padding-right', '2px', 'important');
          }
        }
        if (length == 2){

          var second = $('#'+id+ ' .post_body .img_container:nth-child(2) img')
          console.log('second', 'else', second.height(), second.width())
          if (second.height() > second.width()){
              second.css('height', 'auto');
              second.css('width', '100%');
              second.parent().css('height', divWidth);
              second.parent().css('overflow', 'scroll');
              second.parent().css('padding-left', '2px', 'important');
          }
          var first = $('#'+id+ ' .post_body .img_container:nth-child(1) img')
          if (first.height() > first.width()){
              first.css('height', 'auto');
              first.css('width', '100%');
              first.parent().css('height', divWidth);
              first.parent().css('overflow', 'scroll');
              first.parent().css('padding-right', '2px', 'important');
          }
        }
        if (length == 4){
          $('#'+id+ ' .post_body .img_container:nth-child(2) img').css('padding-left', '4px')
          $('#'+id+ ' .post_body .img_container:nth-child(4) img').css('padding-left', '4px')
          $('#'+id+ ' .post_body .img_container:nth-child(1) img').css('padding-right', '4px')
          $('#'+id+ ' .post_body .img_container:nth-child(3) img').css('padding-right', '4px')
        }
    });
}
