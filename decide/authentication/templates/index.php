{% extends 'base_template.html' %}
{% load i18n static %}

{% block content %}
  <h1 class="text-center">Welcome to Decide Locaste! <br>
    <small class="text-muted">Your web platform for voting</small>
  </h1><br>
    {% if user.is_authenticated %}
    <div class="text-center">
      {% load account %}
      {% user_display user as name %}
      {% blocktrans %}Successfully signed in as {{name}}.{% endblocktrans %}
      <button class="btn btn-outline-danger btn-sm" onClick="decideLogout()">{% trans "Logout" %}</button>
    </div><br>
  {% else %}
    <div class="text-center">
      <button type="button" class="btn btn-outline-primary" value="Sign in" onclick="window.location.href='authentication/sign-in'">Sign in</button>
      <button type="button" class="btn btn-outline-primary" value="Sign up" onclick="window.location.href='authentication/sign-up'">Sign up</button>
    </div>
  {% endif %}
{% endblock %}


{% block extrabody %}
    <script>
        var token = null;
        var user = null;

        function decideUser() {
          var data = { token: token };
          postData("{{auth_url}}" + "/authentication/getuser/", data)
            .then(data => {
              user = data;

            }).catch(error => {
              alert("{% trans "Error: " %}" + error);
            });
        }

        function postData(url, data) {
                // Default options are marked with *
          var fdata = {
            body: JSON.stringify(data),
            headers: {
              'content-type': 'application/json',
            },
            method: 'POST',
          };

          if (token) {
              fdata.headers['Authorization'] = 'Token ' + token;
          }

          return fetch(url, fdata)
          .then(response => {
            if (response.status === 200 || response.status === 201) {
                return response.json();
            } else {
                return Promise.reject(response.statusText);
            }
          });
        }

        function decideLogout() {

          token = null;
          user = null;
          document.cookie = 'decide=; path=/';
          window.location.href = "accounts/logout/";
        }

        function profile(){
          window.location.href = "authentication/profile/"
        }

        function init() {
          var cookies = document.cookie.split("; ");
          cookies.forEach((c) => {
              var cs = c.split("=");
              if (cs[0] == 'decide' && cs[1]) {
                  token = cs[1];
                  decideUser();
              }
          });
        }

        init();

    </script>
    {% endblock %}