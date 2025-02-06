from django.db import models


class Names(models.Model):
    id = models.IntegerField(null=True)
    name = models.CharField(max_length=255, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Names'


class NormalUser(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=45, unique=True, null=True)
    cnpj = models.CharField(max_length=45, unique=True, null=True)
    user_type = models.CharField(max_length=45)
    phone = models.CharField(max_length=25)
    password = models.CharField(max_length=255)
    photo = models.CharField(max_length=255, null=True)
    is_validated = models.BooleanField(default=0)
    is_staff = models.BooleanField(default=0)
    last_pass_change = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'NormalUser'


class UserAuthorization(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    auth = models.TextField()

    class Meta:
        managed = False
        db_table = "UserAuthorization"


class lastPasswords(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.IntegerField()
    password_hash = models.CharField(max_length=255)
    changed_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'lastPasswords'


class UserName(models.Model):
    id = models.IntegerField(primary_key=True)
    name_id = models.IntegerField()
    user_id = models.IntegerField()
    event_id = models.IntegerField()
    create_order = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'UserName'


class userSession(models.Model):
    id = models.IntegerField(primary_key=True)
    user_session = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'UserSession'


class Plans(models.Model):
    id = models.IntegerField(primary_key=True)
    price = models.IntegerField()
    plan_type = models.CharField(max_length=255)
    plan_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Plans'


class Subscription(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    subscription_data = models.DateTimeField(auto_now=True)
    images_allowed = models.IntegerField()
    videos_allowed = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'subscription'


class PlansConfig(models.Model):
    id = models.IntegerField(primary_key=True)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    images_allowed = models.IntegerField()
    videos_allowed = models.BooleanField()
    points_multiplier = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'PlansConfig'


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_final = models.TimeField()
    descricao = models.TextField()
    participantes = models.IntegerField()
    photo = models.ImageField(upload_to='events_photos/',
                              blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/',
                                blank=True, null=True)
    is_active = models.BooleanField(default=0)
    event_creator = models.ForeignKey(NormalUser, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "Event"


class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField()
    question_type = models.TextField()
    event = models.IntegerField()
    photo = models.ImageField(upload_to='questions_photos/',
                              null=True, blank=True)

    class Meta:
        managed = False
        db_table = "questions"


class EventQuestions(models.Model):
    id = models.IntegerField(primary_key=True)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "event_questions"


class ActualQuestion(models.Model):
    id = models.IntegerField(primary_key=True)
    actual_question = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "actual_question"


class Answers(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer_option = models.TextField()
    is_correct = models.BooleanField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "answers"


class EventAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "event_answers"


class UserEvent(models.Model):
    id = models.IntegerField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.IntegerField(null=True, blank=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    cpf = models.CharField(max_length=55, blank=True, null=True)
    cnpj = models.CharField(max_length=55, blank=True, null=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "user_event"


class EventFilter(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = "event_filter"


class EventStatistics(models.Model):
    id = models.IntegerField(primary_key=True)
    event = models.ForeignKey(EventFilter, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE,
                               null=True, blank=True)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answer_text = models.TextField(null=True, blank=True)
    user_event = models.ForeignKey(UserEvent, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "event_statistics"
