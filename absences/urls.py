from django.urls import path # type: ignore
from . import views

urlpatterns = [

    # 🔐 AUTHENTIFICATION
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 📊 DASHBOARDS
    path('admin/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('enseignant/dashboard/', views.dashboard_enseignant, name='dashboard_enseignant'),

    #CLASSES
    path('admin/classes/', views.liste_classes, name='liste_classes'),
    path('admin/classes/ajouter/', views.ajouter_classe, name='ajouter_classe'),
    path('admin/classes/modifier/<int:id_classe>/', views.modifier_classe, name='modifier_classe'),
    path('admin/classes/supprimer/<int:id_classe>/', views.supprimer_classe, name='supprimer_classe'),
    # 👨‍🎓 ÉTUDIANTS
    path('etudiants/', views.liste_etudiants, name='liste_etudiants'),
    path('etudiants/ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
    path('etudiants/modifier/<int:id>/', views.modifier_etudiant, name='modifier_etudiant'),
    path('etudiants/supprimer/<int:id>/', views.supprimer_etudiant, name='supprimer_etudiant'),

    # 👨‍🏫 ENSEIGNANTS
    path('enseignants/', views.liste_enseignant, name='liste_enseignant'),
    path('enseignants/ajouter/', views.ajouter_enseignant, name='ajouter_enseignant'),
    path('enseignants/supprimer/<int:id>/', views.supprimer_enseignant, name='supprimer_enseignant'),
    path('enseignants/modifier/<int:id>/',views.modifier_enseignant,name='modifier_enseignant'),

    # 📝 ABSENCES (ENSEIGNANT)
    path('enseignants/absence/<int:id_enseignant>/',views.ajouter_absence_enseignant,name='ajouter_absence_enseignant'),

    path('absences/ajouter/<int:id_etudiant>/', views.ajouter_absence, name='ajouter_absence'),

    # 📈 STATISTIQUES
    #path('statistiques/', views.statistiques, name='statistiques'),
    path('admin/statistiques/', views.statistique_admin, name='statistique_admin'),
    path('admin/statistiques/enseignants/', views.stats_par_enseignant,name='stats_par_enseignant'),
    path('admin/statistiques/etudiants/',views.stats_etudiants_absents, name='stats_etudiants_absents'),
    path('admin/etudiants/', views.liste_etudiants,name='liste_etudiants_admin'),

    

    # MATIÈRES
    path('matieres/', views.liste_matieres, name='liste_matieres'),
    path('matieres/ajouter/', views.ajouter_matiere, name='ajouter_matiere'),
    path('matieres/modifier/<int:id_matiere>/', views.modifier_matiere, name='modifier_matiere'),
    path('matieres/supprimer/<int:id_matiere>/', views.supprimer_matiere, name='supprimer_matiere'),
    path('enseignant/statistiques/',views.stats_enseignant, name='stats_enseignant' )



]
