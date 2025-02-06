from rest_framework.decorators import api_view  # , throttle_classes
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from ...models import Names, NormalUser, UserName, lastPasswords
from ...serializers.Names import CreateNames, CreateUserName
from ...serializers.NormalUser import UpdateNormalUser, SaveOldPassword
from ...serializers.NormalUser import UpdateaPassword
import jwt
import os
# from ...throttles import DailyRateThrottle, HourlyRateThrottle
# from ...throttles import MinuteRateThrottleAnon
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import transaction
from .user_creation import validate_cnpj, validate_cpf, validate_phoneNumber
from .user_creation import validate_useremail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from dotenv import load_dotenv
import bcrypt
import random
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')


def random_number():
    return str(random.randint(100000, 999999))


@csrf_exempt
@api_view(['PUT'])
# @throttle_classes([MinuteRateThrottleAnon,
#                    HourlyRateThrottle, DailyRateThrottle])
def update_user(request):
    if request.method != 'PUT':
        return JsonResponse({'success': False,
                             'message': 'Invalid request method'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False,
                "message": "Token de acesso não fornecido ou formato inválido."
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('id')

        user = NormalUser.objects.get(id=user_id)
        phone = request.data.get('phone', None)
        cpf = request.data.get('cpf', None)
        cnpj = request.data.get('cnpj', None)
        email = request.data.get('email', None)
        update_name = request.data.get('username')
        if phone:
            validate = validate_phoneNumber(phone)
            if not validate:
                return JsonResponse({"success": False,
                                    "message": "Número de telefone inválido."
                                     }, status=status.HTTP_400_BAD_REQUEST)

        if cpf:
            validate = validate_cpf(cpf)
            if not validate:
                return JsonResponse({"success": False,
                                     "message": "CPF inválido."
                                     }, status=status.HTTP_400_BAD_REQUEST)
        if cnpj:
            validate = validate_cnpj(cnpj)
            if not validate:
                return JsonResponse({"success": False,
                                    "message": "CNPJ inválido."},
                                    status=status.HTTP_400_BAD_REQUEST)
        if email:
            validate = validate_useremail(email)
            if not validate:
                return JsonResponse({"success": False,
                                     "message": "E-mail inválido."
                                     }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            update_user = UpdateNormalUser(user,
                                           data=request.data, partial=True)
            if update_user.is_valid():
                update_user.save()
            else:
                return JsonResponse({'success': False,
                                     'message': 'Invalid data'},
                                    status=status.HTTP_400_BAD_REQUEST)
            username_list = UserName.objects.filter(
                user_id=user.id).order_by('create_order')

            names = []
            for username in username_list:
                try:
                    name_obj = Names.objects.get(id=username.name_id)
                    names.append(name_obj.name)
                except Names.DoesNotExist:
                    continue

            full_name_from_db = " ".join(names).lower().strip()
            update_name = request.data.get('username', '').lower().strip()

            if update_name != full_name_from_db:
                db_name = full_name_from_db.split()
                name_list = update_name.split()

                new_names = [name for name in name_list if name not in db_name]
                rmvd_name = [name for name in db_name if name not in name_list]

                referencias = []
                for new_name in new_names:
                    try:
                        name_obj = Names.objects.get(name=new_name)
                        referencias.append(name_obj.id)
                    except Names.DoesNotExist:
                        name_data = {"name": new_name}
                        serializer = CreateNames(data=name_data)
                        if serializer.is_valid():
                            new_name_obj = serializer.save()
                            referencias.append(new_name_obj.id)
                        else:
                            return JsonResponse({
                                'success': False,
                                'message': 'Erro ao criar novo nome',
                                'error': serializer.errors
                            }, status=status.HTTP_400_BAD_REQUEST)

                if referencias:
                    order = UserName.objects.filter(
                        user_id=user.id).count() + 1
                    for referencia in referencias:
                        serializer_user = CreateUserName(
                            data={'name_id': referencia,
                                  'user_id': user.id,
                                  'create_order': order})
                        if serializer_user.is_valid():
                            serializer_user.save()
                            order += 1
                        else:
                            return JsonResponse({
                                'success': False,
                                'message': 'Erro ao criar nome do usuário',
                                'error': serializer_user.errors
                            }, status=status.HTTP_400_BAD_REQUEST)

                if rmvd_name:
                    for name in rmvd_name:
                        try:
                            name_obj = Names.objects.get(name=name)
                            UserName.objects.filter(user_id=user.id,
                                                    name_id=name_obj.id
                                                    ).delete()
                        except Names.DoesNotExist:
                            continue

        return JsonResponse({'success': True,
                            'message': 'Usuário atualizado com sucesso'},
                            status=status.HTTP_200_OK)

    except NormalUser.DoesNotExist:
        return JsonResponse({'success': False,
                             'message': 'Usuário não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'success': False,
                             'message': 'Erro interno no servidor.',
                             'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
# @throttle_classes([
#     MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def password_reset(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                             'message': 'Método não permitido'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        email = request.data.get('email')
        user = NormalUser.objects.get(email=email)
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"http://127.0.0.1:3000/reset-password/{uid}/{token}/"

        send_mail(
            'Reset your password',
            f'Use the link to reset your password: {reset_url}',
            user.email,
            [user.email],
            fail_silently=False,
        )
        return JsonResponse({"message": "Password reset link sent!"},
                            status=status.HTTP_200_OK)
    except NormalUser.DoesNotExist:
        return JsonResponse({"message": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
# @throttle_classes([
#     MinuteRateThrottleAnon, HourlyRateThrottle, DailyRateThrottle])
def forgot_password(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                             'message': 'Método não permitido'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        email = request.data.get('email')
        user = NormalUser.objects.get(email=email)
        number_random = random_number()
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        base_url = "http://127.0.0.1:3000"
        url = f"{base_url}/forgot-password/{uid}/{token}/{number_random}"

        send_mail(
            'Reset your password',
            f'Use the link to reset your password: {url}',
            user.email,
            [user.email],
            fail_silently=False,
        )
        return JsonResponse({"message": "Password reset link sent!"},
                            status=status.HTTP_200_OK)
    except NormalUser.DoesNotExist:
        return JsonResponse({"message": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.password}"


account_activation_token = TokenGenerator()


@csrf_exempt
@api_view(['POST'])
def password_reset_confirm(request):
    try:
        uidb64 = request.data.get('uid')
        token = request.data.get('token')

        if not uidb64 or not token:
            return JsonResponse({"success": False,
                                 "message": "UID ou Token ausentes."},
                                status=status.HTTP_400_BAD_REQUEST)

        uid = urlsafe_base64_decode(uidb64).decode()
        user = NormalUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, NormalUser.DoesNotExist):
        return JsonResponse({"success": False,
                             "message": "Usuário não encontrado."},
                            status=status.HTTP_400_BAD_REQUEST)

    if user is not None and account_activation_token.check_token(user, token):
        new_password = request.data.get('newPassword')
        old_password = request.data.get('oldPassword')

        if not old_password or not new_password:
            return JsonResponse({"success": False,
                                 "message": "Senhas não fornecidas."},
                                status=status.HTTP_400_BAD_REQUEST)

        actual_password = validate_old_password(old_password, user.password)
        if actual_password is False:
            return JsonResponse({"success": False,
                                 "message": "A senha antiga está incorreta."},
                                status=status.HTTP_400_BAD_REQUEST)

        valid_password = validate_password(new_password)
        if valid_password:
            same_last_password, allow_to_chg = same_password(
                new_password, user.id)
            if same_last_password:
                return JsonResponse({'success': False,
                                     'message':
                                    'Você não pode usar a mesma senha.'},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
            if allow_to_chg:
                password = cript_password(new_password)
                serializer = SaveOldPassword(data={
                    'password_hash': user.password,
                    'user': user.id})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

                new_pass = UpdateaPassword(user, data={'password': password},
                                           partial=True)
                if new_pass.is_valid(raise_exception=True):
                    new_pass.save()
                return JsonResponse({"success": True,
                                     "message": "A senha foi redefinida!"},
                                    status=status.HTTP_200_OK)
    else:
        return JsonResponse({"message": "Token inválido"},
                            status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
def password_forgot_change(request):
    try:
        uidb64 = request.data.get('uid')
        token = request.data.get('token')

        if not uidb64 or not token:
            return JsonResponse({"success": False,
                                 "message": "UID ou Token ausentes."},
                                status=status.HTTP_400_BAD_REQUEST)

        uid = urlsafe_base64_decode(uidb64).decode()
        user = NormalUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, NormalUser.DoesNotExist):
        return JsonResponse({"success": False,
                             "message": "Usuário não encontrado."},
                            status=status.HTTP_400_BAD_REQUEST)

    if user is not None and account_activation_token.check_token(user, token):
        new_password = request.data.get('newPassword')

        valid_password = validate_password(new_password)
        if valid_password:
            same_last_password, allow_to_chg = same_password(
                new_password, user.id)
            if same_last_password:
                return JsonResponse({'success': False,
                                     'message':
                                    'Você não pode usar a mesma senha.'},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
            if allow_to_chg:
                password = cript_password(new_password)
                serializer = SaveOldPassword(data={
                    'password_hash': user.password,
                    'user': user.id})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

                new_pass = UpdateaPassword(user, data={'password': password},
                                           partial=True)
                if new_pass.is_valid(raise_exception=True):
                    new_pass.save()
                return JsonResponse({"success": True,
                                     "message": "A senha foi redefinida!"},
                                    status=status.HTTP_200_OK)
    else:
        return JsonResponse({"message": "Token inválido"},
                            status=status.HTTP_400_BAD_REQUEST)


def validate_old_password(old_password, user_password_hash):
    if old_password is None:
        return False
    return bcrypt.checkpw(
        old_password.encode('utf-8'), user_password_hash.encode('utf-8'))


def validate_password(password):
    if password is None or len(password) < 8:
        return False

    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isnumeric() for char in password)

    if has_upper and has_digit:
        return True
    else:
        False


def cript_password(password):
    if not isinstance(password, str):
        raise ValueError("A senha deve ser uma string.")

    encoded_password = password.encode('utf-8')

    cripted_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
    return cripted_password.decode('utf-8')


def same_password(password, user):
    same_pass = False
    allow_to_change = True
    has_last_passwords = lastPasswords.objects.filter(user=user).exists()
    if has_last_passwords:
        last_password = lastPasswords.objects.filter(user=user)
        for senha_antiga in last_password:
            if bcrypt.checkpw(
                password.encode('utf-8'),
                senha_antiga.password_hash.encode(
                    'utf-8')):
                same_pass = True
                allow_to_change = False
                return same_pass, allow_to_change
    return same_pass, allow_to_change
