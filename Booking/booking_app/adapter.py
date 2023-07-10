from allauth.account.adapter import DefaultAccountAdapter
from .phoneVerification import send

class MyAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        user.email = data["email"]
        user.username = data["username"]
        if "password1" in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        user.save()
        send(user.username)
        return user