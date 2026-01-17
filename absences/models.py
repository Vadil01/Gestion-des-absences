from django.db import models # type: ignore

# Create your models here.

class Classe(models.Model):
    id_classe = models.AutoField(
        primary_key=True,
        db_column='ID_CLASSE'
    )
    nom_classe = models.CharField(
        max_length=50,
        db_column='NOM_CLASSE'
    )
    niveau = models.CharField(
        max_length=20,
        db_column='NIVEAU'
    )

    class Meta:
        managed = False         
        db_table = 'CLASSE'

    def __str__(self):
        return f"{self.nom_classe} - {self.niveau}"


class Etudiant(models.Model):
    id_etudiant = models.IntegerField(primary_key=True)
    matricule = models.CharField(max_length=20)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField()
    id_classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        db_column='ID_CLASSE'
    )

    class Meta:
        db_table = 'ETUDIANT'



class Enseignant(models.Model):
    id_enseignant = models.FloatField(primary_key=True)
    nom = models.CharField(max_length=100, blank=True, null=True)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    id_utilisateur = models.OneToOneField('Utilisateur', models.DO_NOTHING, db_column='id_utilisateur', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'enseignant'



class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)





class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200, blank=True, null=True)
    action_flag = models.IntegerField()
    change_message = models.TextField(blank=True, null=True)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField(blank=True, null=True)
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Matiere(models.Model):
    id_matiere = models.AutoField(primary_key=True, db_column='ID_MATIERE')
    nom_matiere = models.CharField(max_length=100, db_column='NOM_MATIERE')
    enseignant = models.ForeignKey(
        'Enseignant',
        on_delete=models.CASCADE,
        db_column='ID_ENSEIGNANT',
        null=True
    )

    class Meta:
        db_table = 'MATIERE'
        managed = False

    def __str__(self):
        return self.nom_matiere


class Seance(models.Model):
    id_seance = models.IntegerField(primary_key=True, db_column='ID_SEANCE')

    date_seance = models.DateField(db_column='DATE_SEANCE')
    heure_debut = models.DateTimeField(db_column='HEURE_DEBUT')
    heure_fin = models.DateTimeField(db_column='HEURE_FIN')

    id_matiere = models.ForeignKey(
        Matiere,
        on_delete=models.DO_NOTHING,
        db_column='ID_MATIERE'
    )

    id_classe = models.ForeignKey(
        Classe,
        on_delete=models.DO_NOTHING,
        db_column='ID_CLASSE'
    )

    class Meta:
        db_table = 'SEANCE'
        managed = False


class Utilisateur(models.Model):
    id_utilisateur = models.FloatField(primary_key=True)
    login = models.CharField(unique=True, max_length=50)
    mot_de_passe = models.CharField(max_length=255)
    type_role = models.CharField(max_length=20)
    actif = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utilisateur'


class AbsenceEnseignant(models.Model):
    id_ae = models.BigAutoField(
        primary_key=True,
        db_column='ID_AE'
    )

    enseignant = models.ForeignKey(
        Enseignant,
        db_column='ID_ENSEIGNANT',
        on_delete=models.CASCADE
    )

    date_ae = models.DateField(db_column='DATE_AE')
    heure_ae = models.CharField(max_length=5, db_column='HEURE_AE')
    type_ae = models.CharField(max_length=10, db_column='TYPE_AE')
    motif = models.CharField(max_length=200, db_column='MOTIF', blank=True)

    class Meta:
        db_table = 'ABSENCE_ENSEIGNANT'
        managed = False


class AbsenceRetard(models.Model):
    id_ar = models.AutoField(primary_key=True, db_column='ID_AR')

    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.CASCADE,
        db_column='ID_ETUDIANT'
    )

    id_enseignant = models.IntegerField(
        null=True,
        blank=True,
        db_column='ID_ENSEIGNANT'
    )

    matiere = models.CharField(
        max_length=100,
        db_column='MATIERE'
    )

    date_ar = models.DateField(db_column='DATE_AR')
    heure_ar = models.CharField(max_length=5, db_column='HEURE_AR')

    type_ar = models.CharField(max_length=10, db_column='TYPE_AR')
    justifie = models.CharField(max_length=1, db_column='JUSTIFIE')

    class Meta:
        db_table = 'ABSENCE_RETARD'
        managed = False
# models.py


class StatsAbsenceEnseignant(models.Model):
    id_enseignant = models.IntegerField()
    enseignant = models.CharField(max_length=100)
    nom_matiere = models.CharField(max_length=100)
    total = models.IntegerField()
    total_absences = models.IntegerField()
    total_retards = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'V_STATS_ABS_ENSEIGNANT'
