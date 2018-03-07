
function img_upload(callback) {
    input = $('#my-file')[0]
    var files_array = []
    var numFiles = input.files.length;
    console.log('dmytrooo2', input, numFiles)
    if (input.files && input.files[0]) {

      var reader0 = new FileReader();
      console.log('dmytrooo21', reader0)

      var form_data = new FormData($('#post_form')[0]);

          
      for (var value of form_data.values()) {
        console.log('infunc', value)
         
      }
      callback(form_data); 

      // reader.readAsDataURL(input.files[0]);
    }else{
      callback(undefined); 
    }
}

$(document).on('change', '#my-file', function(e) {
    var form_data = new FormData($('#post_form')[0]);
    var value
          
    // for (var value of form_data.values()) {
    //   console.log('infunc', value)
       
    // }
    for (var pair of form_data.entries()) {
      console.log(pair[0]+ ', ' + pair[1]); 
    }

    console.log('dmytrooo', form_data, form_data.values())
    // img_upload(function(result){
    //   form_data = result
    //   console.log('heyhey',  form_data);
    // });


})


$(document).on('click', '.post_btn', function(e) {
    e.preventDefault()

    

    var text = $('.create_post_textarea').html()
    text = text.split('')
    var image_being = $('.post_images').length


    var delete_cur
    var aditional = 0
    var array_length = text.length
    for (var i = 0; i <= text.length - 1 + aditional ; i++) {
        aditional = array_length - text.length
        if (text[i-aditional] == '<'){
            delete_cur = i-aditional
        }else if (text[i-aditional] == '>'){
            text.splice(delete_cur, i-aditional - delete_cur + 1)
        }
    }
    for (var i = 0; i <= text.length - 1 + aditional ; i++) {
        aditional = array_length - text.length
        if (text[i-aditional] == '<'){
            delete_cur = i-aditional
        }else if (text[i-aditional] == '>'){
            text.splice(delete_cur, i-aditional - delete_cur + 1)
        }
    }
    console.log(text)
    if (text.length == 0 && image_being == 1) {
      console.log('leer')
      return
    }
    modal.style.display = "none";

    text = text.join('');

    console.log('1')
    img_upload(function(result){
      form_data = result
      console.log('heyhey',  form_data);

      

      city = $('.place_check').html();
      var tags_array = [];

    $('.create_post_textarea .hastag_changed').each(function(){
         console.log('found!')
        tags_array.push($(this).val())
    });

      if (form_data != undefined) {

          for (var value of form_data.values()) {
            console.log('outfunc', value)
             
          }
          
          form_data.append('text', text)
          form_data.append('tags', tags_array)
          form_data.append('location', city)
          form_data.append('date', new Date().toLocaleString())

          $.ajax({
                type: 'POST',
                url: '/post' ,
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                async: false,
                success: function(response) {
                    console.log(response.status, response.post_id, 'searching');
                    $('#new_posts_status').text(response.post_id)
                },
                error: function(error) {
                    console.log(error);
                }
            });
      }else{
          console.log('else')
          var form_data = new FormData($('#post_form')[0]);

          form_data.append('text', text)
          form_data.append('tags', tags_array)
          form_data.append('location', city)
          form_data.append('date', new Date().toLocaleString())

          $.ajax({
                type: 'POST',
                url: '/post' ,
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                async: false,
                success: function(response) {
                    console.log(response.status, response.post_id, 'searching');
                    $('#new_posts_status').text(response.post_id)
                    
                },
                error: function(error) {
                    console.log(error);
                }
            });
      }




      $("body").css("overflow", "auto");

      $('.place_check').addClass('none')
      $('.default_text').removeClass('none')

      $('.create_post_images').empty()

      $( "#trigger_class" ).trigger( "click" );

      $('.alert').addClass('appear_alert')

      setTimeout(function(){
        $('.alert').removeClass('appear_alert')
        $('.alert').addClass('hide_alert')
      },2000);
      setTimeout(function(){
        $('.alert').removeClass('hide_alert')
      },2500);
    });
    
    
});


// Get the modal
var modal = document.getElementById('myModal');

// Get the button that opens the modal
var btn2 = document.getElementById("myBtn2");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal

btn2.onclick = function() {
    modal.style.display = "block";
    $("body").css("overflow", "hidden");
}



span.onclick = function() {
    var warn = confirm("Delete this post?");
    if (warn == true) {
        modal.style.display = "none";
        $("body").css("overflow", "auto");

        $('.place_check').addClass('none')
        $('.default_text').removeClass('none')

        $('.create_post_images').empty()

        $( "#trigger_class" ).trigger( "click" );
    } else {

    }

}

// empty all inputs
$('#trigger_class').on('click', function(e){
   var $el = $('#my-file');
   $el.wrap('<form>').closest('form').get(0).reset();
   $el.unwrap();

    $('.create_post_textarea').html('')
    $('.create_post_textarea').css('height', 'auto')
    $('.img_num').html(4)

});


// When the user clicks anywhere outside of the modal, close it


jQuery.each(jQuery('textarea[data-autoresize]'), function() {
    var offset = this.offsetHeight - this.clientHeight;

    var resizeTextarea = function(el) {
        jQuery(el).css('height', 'auto').css('height', el.scrollHeight + offset);
    };
    jQuery(this).on('keyup input', function() { resizeTextarea(this); }).removeAttr('data-autoresize');
});


//insert tag

$(document).on('keyup', '.post_text_edit', function(e) {
    $(e.target).remove()
    $('.create_post_textarea').focus()
});

  // searching for hastag
$(document).on('keyup', '.create_post_textarea', function(e) {
    var post_array = []
    var post_text = $('.create_post_textarea').html()
    post_text = post_text.replace(/<br>/g,'');
    post_text = post_text.replace(/&nbsp;/g,'');
    for (var i = 0, len = post_text.length; i < len; i++) {
      post_array.push(post_text.charAt(i))
      if ((post_text.charAt(i) == '#') && (post_text.charAt(i-2) != '' && post_text.charAt(i-1) != '>' || post_text.charAt(i+1) != '<')){
        insertTag(i)
        $('.choose_tag_input').focus();
      }
    }
});
$(document).on('keyup', 'input[name=tag]', function(e) {
    var post_text = $('input[name=tag]').val()
    post_text = post_text.replace(/#/g,'');
    $('input[name=tag]').val(post_text)
});
$(document).on('change', '.fa-select', function(e) {
    $('input[name=tag]').focus()
});

function insertTag(index){
    $(".create_post_textarea").html(function(i,v){
      console.log(v)
      data = v.replace(/>#</g,'><');
      console.log(data)
      return data.replace(/#/g , '<div class="choose_tag" contenteditable="false"><select class="fa-select" name="hash_selector"><option value="hash">#</option><option value="laugh">😂</option><option value="wow">😯</option><option value="smile">🙂</option><option value="applause">👏</option></select><input type="text" name="tag" placeholder="Hastag" class="choose_tag_input"><p class="ok">OK</p><p class="cancel">CANCEL</p></div>' )
    });
}
$('.create_post_textarea').on('keypress', function(e) {
   if(e.which == 13) {
        var hashtag = $('select[name=hash_selector]').val()
        var insert = hashtag
        var input = $('input[name=tag]').val()
        console.log(hashtag)
        if (input == undefined){
          return
        }
        if (input == ''){
          return  $(e.target).parent().replaceWith('')
        }
        $("body").bind("DOMNodeInserted", function() {
           prependClass($(this).find('.hastag_changed'), '_'+insert+'-')
        });
        if (hashtag == 'hash'){
          hashtag = '&#xf292;'
        }
        if (hashtag == 'laugh'){
          hashtag = '😂'
        }
        if (hashtag == 'wow'){
          hashtag = '😯'
        }
        if (hashtag == 'smile'){
          hashtag = '🙂'
        }
        if (hashtag == 'applause'){
          hashtag = '👏'
        }

        $(e.target).parent().replaceWith('<input class="hastag_changed autoresize" contenteditable="true" value="'+ hashtag + input + '"></input><input class="post_text_edit" contenteditable="true"> </input>')
        // var $input = $('.hastag_changed'),
        //     $buffer = $('.input-buffer');

        // $buffer.text($input.val());
        // $input.width($buffer.width());

        $('.hastag_changed').attr('size', $('.hastag_changed').val().length);
        $('.post_text_edit').focus()



    $(".create_post_textarea").val($(".create_post_textarea").val())
    console.log(hashtag, input, $(e.target).parent())
    }
});


$(document).on('click', '.ok', function(e) {
    var hashtag = $('select[name=hash_selector]').val()
    var insert = hashtag
    var input = $('input[name=tag]').val()
    if (input == ''){
      return  $(e.target).parent().replaceWith('')
    }
    $("body").bind("DOMNodeInserted", function() {
      prependClass($(this).find('.hastag_changed'), '_'+insert+'-')
    });
    if (hashtag == 'hash'){
      hashtag = '&#xf292;'
    }
    if (hashtag == 'laugh'){
      hashtag = '😂'
    }
    if (hashtag == 'wow'){
      hashtag = '😯'
    }
    if (hashtag == 'smile'){
      hashtag = '🙂'
    }
    if (hashtag == 'applause'){
      hashtag = '👏'
    }
    $(e.target).parent().replaceWith('<input class="hastag_changed autoresize" contenteditable="true" value="'+ hashtag + input + '"></input>')
    $('.hastag_changed').attr('size', $('.hastag_changed').val().length);
    $('.create_post_textarea').focus()
    $(".create_post_textarea").val($(".create_post_textarea").val())
    console.log(hashtag, input, $(e.target).parent())
});

function prependClass(sel, strClass) {
    var $el = sel
    console.log($el, strClass)
    /* prepend class */
    var classes = $el.attr('class');
    classes = strClass +' ' +classes;
    $el.removeClass()
    $el.attr('class', classes);
}

$(document).on('focusin', '.hastag_changed', function(e) {
    var text = $('.hastag_changed').attr('value').substring(1, $('.hastag_changed').attr('value').length)
    var option = 'hash'
    var emotion = $(".hastag_changed[class^='_'],.hastag_changed[class*='-']").attr('class').split(' ')[0].slice(1,-1)
    if(emotion!='hash'){
      text = $('.hastag_changed').attr('value').substring(2, $('.hastag_changed').attr('value').length)
    }

    console.log(emotion, option)
    var input = $('input[name=tag]').val()

    $(e.target).replaceWith('<div class="choose_tag" contenteditable="false"><select class="fa-select" name="hash_selector"><option value="hash">#</option><option value="laugh">😂</option><option value="wow">😯</option><option value="smile">🙂</option><option value="applause">👏</option></select><input type="text" class="choose_tag_input" name="tag" placeholder="Hastag" value="'+ text +'"><p class="ok">OK</p><p class="cancel">CANCEL</p></div>')
    $('input[name=tag]').focus()
    var val = $('input[name=tag]').val();
    $('input[name=tag]').val('');
    $('input[name=tag]').val(val);

    $("select[name=hash_selector]").val(emotion);
});

$(document).on('click', '.cancel', function(e) {
    $(e.target).parent().replaceWith('')
});

$(document).mouseup(function(e) {
    var container = $(".choose_tag_input").parent();

    // if the target of the click isn't the container nor a descendant of the container
    if (!container.is(e.target) && container.has(e.target).length === 0)
    {
        container.remove();
    }
});

