from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.db import connection, IntegrityError # type: ignore
import absences # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from .utils import enseignant_required
from .utils import admin_required, login_required_custom
from .models import Enseignant,Seance, AbsenceRetard,Etudiant, Classe, Matiere
from django.contrib import messages # type: ignore
from django.db.models import Count # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.http import HttpResponseForbidden # type: ignore

from .models import (
    Utilisateur,
    Etudiant,
    Enseignant,
    Classe,
    AbsenceRetard
)

from .models import (
    Etudiant,
    Enseignant,
    AbsenceRetard,
    AbsenceEnseignant
)



# =========================
# 🔐 AUTHENTIFICATION
# =========================

def login_view(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')

        # Vérification dans Oracle
        user = Utilisateur.objects.filter(
            login=login,
            mot_de_passe=password,
            actif='O'
        ).first()

        if user:
            request.session['user_id'] = user.id_utilisateur
            request.session['role'] = user.type_role

            if user.type_role == 'ADMIN':
                return redirect('dashboard_admin')
            elif user.type_role == 'ENSEIGNANT':
                return redirect('dashboard_enseignant')

        return render(request, 'absences/login.html', {
            'error': 'Login ou mot de passe incorrect'
        })

    return render(request, 'absences/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# =========================
# 📊 DASHBOARDS
# =========================



@admin_required
def dashboard_admin(request):

    stats_matiere = (
        AbsenceRetard.objects
        .values('matiere')
        .annotate(total=Count('id_ar'))
        .order_by('-total')
    )

    context = {
        'total_etudiants': Etudiant.objects.count(),
        'total_enseignants': Enseignant.objects.count(),
        'total_absences': AbsenceRetard.objects.count(),
        'stats_matiere': stats_matiere,
    }

    return render(request, 'absences/dashboard_admin.html', context)


@login_required_custom
def dashboard_enseignant(request):
    return render(request, 'absences/dashboard_enseignant.html')


# =========================
# 👨‍🎓 ÉTUDIANTS (ADMIN)
# =========================



@login_required_custom
def liste_etudiants(request):
    etudiants = Etudiant.objects.all()
    role = request.session.get('role')

    if role == 'ADMIN':
        template = 'absences/liste_etudiants_admin.html'
    else:
        template = 'absences/liste_etudiants_enseignant.html'

    return render(request, template, {
        'etudiants': etudiants
    })


@admin_required
def ajouter_etudiant(request):
    classes = Classe.objects.all()

    if request.method == 'POST':
        Etudiant.objects.create(
            matricule=request.POST.get('matricule'),
            nom=request.POST.get('nom'),
            prenom=request.POST.get('prenom'),
            email=request.POST.get('email'),
            id_classe_id=request.POST.get('id_classe')
        )
        return redirect('liste_etudiants_admin')

    return render(request, 'absences/ajouter_etudiants.html', {
        'classes': classes
    })


@admin_required
def modifier_etudiant(request, id):
    etudiant = get_object_or_404(Etudiant, id_etudiant=id)
    classes = Classe.objects.all()

    if request.method == 'POST':
        etudiant.matricule = request.POST['matricule']
        etudiant.nom = request.POST['nom']
        etudiant.prenom = request.POST['prenom']
        etudiant.email = request.POST['email']
        etudiant.id_classe_id = request.POST['id_classe']
        etudiant.save()

        return redirect('liste_etudiants_admin')

    return render(request, 'absences/modifier_etudiants.html', {
        'etudiant': etudiant,
        'classes': classes
    })


@admin_required
def supprimer_etudiant(request, id):
    etudiant = get_object_or_404(Etudiant, id_etudiant=id)
    etudiant.delete()
    return redirect('liste_etudiants_admin')


# =========================
# 👨‍🏫 ENSEIGNANTS (ADMIN)
# =========================


@admin_required
def modifier_enseignant(request, id):
    enseignant = get_object_or_404(Enseignant, id_enseignant=id)

    if request.method == 'POST':
        enseignant.nom = request.POST['nom']
        enseignant.prenom = request.POST['prenom']
        enseignant.email = request.POST['email']
        enseignant.save()   # UPDATE Oracle

        return redirect('liste_enseignant')

    return render(request, 'absences/modifier_enseignant.html', {
        'enseignant': enseignant
    })

@admin_required
def liste_enseignant(request):
    enseignants = Enseignant.objects.all()
    return render(request, 'absences/liste_enseignant.html', {
        'enseignants': enseignants
    })


@admin_required
def ajouter_enseignant(request):
    if request.method == 'POST':
        Enseignant.objects.create(
            nom=request.POST['nom'],
            prenom=request.POST['prenom'],
            email=request.POST['email']
        )
        return redirect('liste_enseignant')

    return render(request, 'absences/Ajouter_enseignant.html')

@admin_required
def supprimer_enseignant(request, id):
    enseignant = get_object_or_404(Enseignant, id_enseignant=id)

    if enseignant.matiere_set.exists():
        messages.error(
            request,
            "❌ Impossible de supprimer cet enseignant : "
            "des matières lui sont encore associées."
        )
        return redirect('liste_enseignant')

    enseignant.delete()
    messages.success(request, "✅ Enseignant supprimé avec succès.")
    return redirect('liste_enseignant')




# =========================
# 📝 ABSENCES (ENSEIGNANT)
# =========================
# absences/views.py
@admin_required
def ajouter_absence_enseignant(request, id_enseignant):
    enseignant = get_object_or_404(Enseignant, id_enseignant=id_enseignant)

    if request.method == 'POST':
        # 🔒 Sécurisé : évite MultiValueDictKeyError
        date_ae = request.POST.get('date_ae')
        heure_ae = request.POST.get('heure_ae')
        type_ae = request.POST.get('type_ae')
        motif = request.POST.get('motif', '')

        if not date_ae or not heure_ae or not type_ae:
            messages.error(request, "❌ Tous les champs obligatoires doivent être remplis.")
            return redirect(request.path)

        AbsenceEnseignant.objects.create(
            enseignant=enseignant,   # ✅ PAS id_enseignant
            date_ae=date_ae,
            heure_ae=heure_ae,
            type_ae=type_ae,
            motif=motif
        )

        messages.success(request, "✅ Absence ajoutée avec succès.")
        return redirect('liste_enseignant')

    return render(request, 'absences/ajouter_absence_enseignant.html', {
        'enseignant': enseignant
    })



def ajouter_absence(request, id_etudiant):
    etudiant = get_object_or_404(Etudiant, id_etudiant=id_etudiant)

    if request.method == 'POST':
        matiere = request.POST.get('matiere')
        date_ar = request.POST.get('date_ar')
        heure_ar = request.POST.get('heure_ar')

        if not all([matiere, date_ar, heure_ar]):
            messages.error(request, "❌ Tous les champs sont obligatoires")
            return redirect(request.path)

        AbsenceRetard.objects.create(
            etudiant=etudiant,
            matiere=matiere,
            date_ar=date_ar,
            heure_ar=heure_ar,
            type_ar='ABSENCE',
            justifie='N',
            id_enseignant=None   # ✅ Oracle accepte NULL
        )

        messages.success(request, "✅ Absence ajoutée avec succès")
        return redirect('liste_etudiants')

    return render(request, 'absences/ajouter_absence.html', {
        'etudiant': etudiant
    })



@enseignant_required
def ajouter_absence_etudiant(request, id_etudiant):
    if request.method == 'POST':
        AbsenceRetard.objects.create(
            id_etudiant=id_etudiant,
            id_seance=request.POST['seance'],
            motif=request.POST['motif']
        )
        return redirect('liste_etudiants_enseignant')

    return render(request, 'absences/ajouter_absence.html')






# =========================
# 📈 STATISTIQUES (ORACLE)
# =========================
@admin_required
def statistique_admin(request):
    with connection.cursor() as cursor:

        # 📅 Par jour
        cursor.execute("""
            SELECT DATE_AR, COUNT(*)
            FROM ABSENCE_RETARD
            GROUP BY DATE_AR
            ORDER BY DATE_AR
        """)
        stats_jour = cursor.fetchall()

        # 🗓️ Par mois
        cursor.execute("""
            SELECT TO_CHAR(DATE_AR, 'MM-YYYY'), COUNT(*)
            FROM ABSENCE_RETARD
            GROUP BY TO_CHAR(DATE_AR, 'MM-YYYY')
            ORDER BY TO_CHAR(DATE_AR, 'MM-YYYY')
        """)
        stats_mois = cursor.fetchall()

        # 🎓 Par année universitaire
        cursor.execute("""
            SELECT TO_CHAR(DATE_AR, 'YYYY'), COUNT(*)
            FROM ABSENCE_RETARD
            GROUP BY TO_CHAR(DATE_AR, 'YYYY')
            ORDER BY TO_CHAR(DATE_AR, 'YYYY')
        """)
        stats_annee = cursor.fetchall()

        # 📚 Par matière
        cursor.execute("""
            SELECT m.nom_matiere, COUNT(*)
            FROM ABSENCE_RETARD ar
            JOIN SEANCE s ON ar.id_seance = s.id_seance
            JOIN MATIERE m ON s.id_matiere = m.id_matiere
            GROUP BY m.nom_matiere
        """)
        stats_matiere = cursor.fetchall()

    return render(request, 'absences/statistique_admin.html', {
        'stats_jour': stats_jour,
        'stats_mois': stats_mois,
        'stats_annee': stats_annee,
        'stats_matiere': stats_matiere,
    })


@admin_required
def stats_par_enseignant(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.nom, e.prenom, COUNT(ar.id_ar)
            FROM absence_retard ar
            JOIN enseignant e ON ar.id_enseignant = e.id_enseignant
            GROUP BY e.nom, e.prenom
            ORDER BY COUNT(ar.id_ar) DESC
        """)
        stats = cursor.fetchall()

    return render(
        request,
        'absences/stats_enseignant.html',
        {'stats': stats}
    )

@admin_required
def stats_etudiants_absents(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                e.matricule,
                e.nom,
                e.prenom,
                ens.nom || ' ' || ens.prenom AS enseignant,
                COUNT(ar.id_ar) AS total_absences
            FROM ABSENCE_RETARD ar
            JOIN ETUDIANT e
                ON ar.id_etudiant = e.id_etudiant
            JOIN ENSEIGNANT ens
                ON ar.id_enseignant = ens.id_enseignant
            GROUP BY
                e.matricule,
                e.nom,
                e.prenom,
                ens.nom,
                ens.prenom
            ORDER BY total_absences DESC
        """)
        stats = cursor.fetchall()

    return render(
        request,
        'absences/stats_etudiants.html',
        {'stats': stats}
    )


def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('role'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper





# 📋 LISTE DES ÉTUDIANTS
# ADMIN + ENSEIGNANT


# 📋 LISTE DES CLASSE


@admin_required
def liste_classes(request):
    classes = Classe.objects.all().order_by('nom_classe')
    return render(request, 'absences/liste_classes.html', {
        'classes': classes
    })




@admin_required
def ajouter_classe(request):
    if request.method == 'POST':
        nom = request.POST.get('nom_classe')
        niveau = request.POST.get('niveau')

        # 🔒 Vérification AVANT insertion (UX propre)
        if Classe.objects.filter(
            nom_classe=nom,
            niveau=niveau
        ).exists():
            messages.error(
                request,
                "❌ Classe déjà existante (même nom et niveau)."
            )
            return redirect('ajouter_classe')

        try:
            Classe.objects.create(
                nom_classe=nom,
                niveau=niveau
            )
            messages.success(
                request,
                "✅ Classe ajoutée avec succès."
            )
            return redirect('liste_classes')

        except IntegrityError:
            # 🔒 Sécurité finale (Oracle reste maître)
            messages.error(
                request,
                "❌ Impossible d’ajouter la classe (doublon détecté)."
            )

    return render(request, 'absences/ajouter_classe.html')


@admin_required
def modifier_classe(request, id_classe):
    classe = get_object_or_404(Classe, pk=id_classe)

    if request.method == 'POST':
        classe.nom_classe = request.POST['nom_classe']
        classe.niveau = request.POST['niveau']
        classe.save()
        return redirect('liste_classes')

    return render(request, 'absences/modifier_classe.html', {
        'classe': classe
    })


@admin_required
def supprimer_classe(request, id_classe):
    classe = get_object_or_404(Classe, pk=id_classe)

    # 🔒 Vérifier s'il existe des séances liées
    if classe.seance_set.exists():
        messages.error(
            request,
            "❌ Impossible de supprimer cette classe : "
            "elle est déjà utilisée dans des séances."
        )
        return redirect('liste_classes')

    classe.delete()
    messages.success(request, "✅ Classe supprimée avec succès.")
    return redirect('liste_classes')




# 📌 LISTE DES MATIÈRES
def liste_matieres(request):
    matieres = Matiere.objects.select_related('enseignant')
    return render(request, 'absences/liste_matiers.html', {
        'matieres': matieres
    })


# ➕ AJOUTER MATIÈRE

def ajouter_matiere(request):
    enseignants = Enseignant.objects.all()

    if request.method == 'POST':
        nom = request.POST.get('nom_matiere')
        enseignant_id = request.POST.get('enseignant')

        # 🔍 Vérification doublon
        existe = Matiere.objects.filter(
            nom_matiere__iexact=nom,
            enseignant_id=enseignant_id
        ).exists()

        if existe:
            messages.error(
                request,
                "Cette matière existe déjà pour cet enseignant."
            )
        else:
            Matiere.objects.create(
                nom_matiere=nom,
                enseignant_id=enseignant_id
            )
            messages.success(request, "Matière ajoutée avec succès.")
            return redirect('liste_matiers')

    return render(request, 'absences/ajouter_matier.html', {
        'enseignants': enseignants
    })




# ✏️ MODIFIER MATIÈRE

def modifier_matiere(request, id_matiere):
    matiere = get_object_or_404(Matiere, pk=id_matiere)

    # 🔹 Tous les enseignants depuis Oracle
    enseignants = Enseignant.objects.all().order_by('nom')

    if request.method == 'POST':
        nom = request.POST.get('nom_matiere')
        id_enseignant = request.POST.get('enseignant')

        matiere.nom_matiere = nom

        if id_enseignant:
            matiere.enseignant = get_object_or_404(
                Enseignant,
                pk=id_enseignant
            )
        else:
            matiere.enseignant = None

        matiere.save()

        messages.success(request, "✅ Matière modifiée avec succès.")
        return redirect('liste_matiers')

    return render(request, 'absences/modifier_matier.html', {
        'matiere': matiere,
        'enseignants': enseignants
    })


# 🗑️ SUPPRIMER MATIÈRE
def supprimer_matiere(request, id_matiere):
    matiere = get_object_or_404(Matiere, pk=id_matiere)
    matiere.delete()

    messages.success(request, "🗑️ Matière supprimée.")
    return redirect('liste_matiers')
