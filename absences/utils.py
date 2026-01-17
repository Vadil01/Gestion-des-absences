from django.shortcuts import redirect # type: ignore

# 🔐 ADMIN SEULEMENT

def admin_required(view):
    def wrapper(request, *args, **kwargs):
        if request.session.get('role') != 'ADMIN':
            return redirect('login')
        return view(request, *args, **kwargs)
    return wrapper


# 🔐 ADMIN + ENSEIGNANT
def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('role'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def enseignant_required(view):
    def wrapper(request, *args, **kwargs):
        if request.session.get('role') != 'ENSEIGNANT':
            return redirect('login')
        return view(request, *args, **kwargs)
    return wrapper


from django.shortcuts import redirect
from django.contrib import messages

def enseignant_required(view_func):
    def wrapper(request, *args, **kwargs):

        # 🔒 1. Vérifier connexion
        if not request.user.is_authenticated:
            messages.error(request, "Veuillez vous connecter.")
            return redirect('login')

        # 🔒 2. Vérifier lien enseignant
        if not hasattr(request.user, 'enseignant'):
            messages.error(request, "Accès réservé aux enseignants.")
            return redirect('dashboard_enseignant')

        return view_func(request, *args, **kwargs)

    return wrapper
