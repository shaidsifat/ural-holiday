from django.contrib.auth.decorators import user_passes_test

def phone_verification_required(f):
    return user_passes_test(lambda u: u.is_phone_verified, login_url='/phone-verification')(f)

def phone_verification_not_required(f):
    return user_passes_test(lambda u: not u.is_phone_verified, login_url='/my-account')(f)