$(document).ready(function () {
  $('#loginForm').on('submit', function (e) {
    e.preventDefault();

    let username = $('#username').val().trim();
    let password = $('#password').val().trim();
    let errorMsg = '';

    if (username === '' || password === '') {
      errorMsg = 'All fields are required.';
    } else if (password.length < 8) {
      errorMsg = 'Password must be at least 8 characters long.';
    }

    if (errorMsg) {
      $('#error').text(errorMsg);
    } else {
      this.submit();
    }
  });

  $('input').on('input', function () {
    $('#error').text('');
  });
    // Password toggle functionality
    $("#password-toggle").on("click", function () {
      const passwordInput = $("#password");
      const icon = $(this).find("i");
  
      if (passwordInput.attr("type") === "password") {
        passwordInput.attr("type", "text");
        icon.removeClass("fa-eye").addClass("fa-eye-slash");
      } else {
        passwordInput.attr("type", "password");
        icon.removeClass("fa-eye-slash").addClass("fa-eye");
      }
    });
});
