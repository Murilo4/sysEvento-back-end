from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from ...models import Names, NormalUser
from ...serializers.Names import CreateNames, CreateUserName
from ...serializers.NormalUser import CreateNormalUser
from ...serializers.NormalUser import CreateAuthorizationEvents
import re
from django.db import transaction
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from django.conf import settings


@api_view(['POST'])
def create_user(request):
    if request.method != 'POST':
        return JsonResponse({"success": False,
                             "message": "Invalid request method"},
                            status=status.HTTP_400_BAD_REQUEST)

    userName: str = request.data.get("username")
    email: str = request.data.get("email")
    phone = request.data.get("phone")
    password = request.data.get("password")
    cpf = request.data.get("cpf") if request.data.get("cpf") else None
    cnpj = request.data.get("cnpj") if request.data.get("cnpj") else None

    if not userName:
        return JsonResponse({"success": False,
                             "message": "User name is required"},
                            status=status.HTTP_400_BAD_REQUEST)
    with transaction.atomic():
        if cpf is not None:
            validate = validate_cpf(cpf)
            if validate is False:
                return JsonResponse({"success": False,
                                    "message": "CPF invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)
            validate_user = validate_username(userName)
            if validate_user is False:
                return JsonResponse({"success": False,
                                    "message": "Nome invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)

            validate_phone = validate_phoneNumber(phone)

            if validate_phone is False:
                return JsonResponse({"success": False,
                                    "message": "Número de telefone invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)

            validate_email = validate_useremail(email)

            if validate_email is False:
                return JsonResponse({"success": False,
                                    "message": "Email invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)

            validete_pass = validate_password(password)
            if validete_pass is False:
                return JsonResponse({"success": False,
                                    "message": "Senha invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)

            cripted_password = cript_password(password)
            if cripted_password is None:
                return JsonResponse({"success": False,
                                    "message": "Erro ao criptografar a senha"},
                                    status=status.HTTP_400_BAD_REQUEST)

            userName = userName.strip()

            name = [n.lower().strip() for n in userName.split() if n.strip()]

            created_names, referencias = create_names(name)

            if created_names is False:
                return JsonResponse({
                    "success": False,
                    "message": "Erro ao criar nome",
                }, status=status.HTTP_400_BAD_REQUEST)

            numeros_cpf = re.sub(r'\D', '', cpf)
            user_create = CreateNormalUser(
                data={'email': email,
                      'phone': phone,
                      'user_type': 'Normal',
                      'password': cripted_password,
                      'cpf': numeros_cpf,
                      'photo': request.data.get('photo', None),
                      'last_pass_change': datetime.now(),
                      })

            if user_create.is_valid(raise_exception=True):
                user_create.save()
                get_user = NormalUser.objects.get(cpf=numeros_cpf)
                user_id = get_user.id
                order = 1
                for referencia in referencias:
                    serializer_user = CreateUserName(
                        data={'name_id': referencia,
                              'user_id': user_id,
                              'create_order': order})

                    if serializer_user.is_valid(raise_exception=True):
                        serializer_user.save()
                        order += 1
                    else:
                        return JsonResponse({"sucess": False,
                                            "message":
                                             "Erro ao criar nome do usuario"},
                                            status=status.HTTP_400_BAD_REQUEST)

                auth = {
                    "user": get_user.id,
                    "auth": "SysEventos"
                }
                create_auth = CreateAuthorizationEvents(data=auth)
                if create_auth.is_valid():
                    create_auth.save()

                    token = generate_jwt(get_user.email)
                    return JsonResponse({"success": True,
                                        "message":
                                         "Usuario criado com sucesso",
                                         "token": token},
                                        status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({
                    "success": False,
                    "message": "Erro ao criar usuario",
                })
        elif cnpj is not None:
            validate = validate_cnpj(cnpj)
            if validate is False:
                return JsonResponse({"sucess": False,
                                    "message": "CNPJ invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)

            validate_user = validate_username(userName)
            if validate_user is False:
                return JsonResponse({"success": False,
                                    "message": "Nome invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)

            validate_phone = validate_phoneNumber(phone)

            if validate_phone is False:
                return JsonResponse({"success": False,
                                    "message": "Número de telefone invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)

            validate_email = validate_useremail(email)

            if validate_email is False:
                return JsonResponse({"success": False,
                                    "message": "Email invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)

            validete_pass = validate_password(password)
            if validete_pass is False:
                return JsonResponse({"success": False,
                                    "message": "Senha invalido"},
                                    status=status.HTTP_400_BAD_REQUEST)

            cripted_password = cript_password(password)
            if cripted_password is None:
                return JsonResponse({"success": False,
                                    "message": "Erro ao criptografar a senha"},
                                    status=status.HTTP_400_BAD_REQUEST)

            userName = userName.strip()

            name = [n.lower().strip() for n in userName.split() if n.strip()]

            created_names, referencias = create_names(name)

            if created_names is False:
                return JsonResponse({
                    "success": False,
                    "message": "Erro ao criar nome",
                }, status=status.HTTP_400_BAD_REQUEST)

            numeros_cnpj = re.sub(r'\D', '', cnpj)
            user_create = CreateNormalUser(
                data={'email': email,
                      'phone': phone,
                      'user_type': 'Enterprise',
                      'password': cripted_password,
                      'cnpj': numeros_cnpj,
                      'photo': request.data.get("photo", None),
                      'last_pass_change': datetime.now(),
                      })

            if user_create.is_valid(raise_exception=True):
                user_create.save()
                get_user = NormalUser.objects.get(cnpj=numeros_cnpj)
                user_id = get_user.id
                order = 1
                for referencia in referencias:
                    link_name = Names.objects.get(id=referencia)
                    serializer_user = CreateUserName(
                        data={'name_id': link_name.id,
                              'user_id': user_id,
                              'create_order': order})

                    if serializer_user.is_valid(raise_exception=True):
                        serializer_user.save()
                        order += 1
                    else:
                        return JsonResponse({"success": False,
                                            "message":
                                             "Erro ao criar nome do usuario"},
                                            status=status.HTTP_400_BAD_REQUEST)
                auth = {
                    "user": get_user.id,
                    "auth": "SysEventos"
                }
                create_auth = CreateAuthorizationEvents(data=auth)
                if create_auth.is_valid():
                    create_auth.save()

                    token = generate_jwt(get_user.email)
                    return JsonResponse({"success": True,
                                        "message":
                                         "Usuario criado com sucesso",
                                         "token": token},
                                        status=status.HTTP_201_CREATED)

        else:
            return JsonResponse({"success": False,
                                 "message": "Erro ao criar usuario"},
                                status=status.HTTP_400_BAD_REQUEST)


def validate_cpf(cpf):
    numbers = [int(digit) for digit in cpf if digit.isdigit()]
    if len(numbers) != 11 or len(set(numbers)) == 1:
        return False

    sum_of_products = sum(
        a*b for a, b in zip(numbers[0:9], range(10, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[9] != expected_digit:
        return False
    sum_of_products = sum(
        a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[10] != expected_digit:
        return False

    return True


def validate_cnpj(cnpj):
    LENGTH_CNPJ = 14
    cnpj = ''.join(filter(str.isdigit, cnpj))

    if len(cnpj) != LENGTH_CNPJ:
        return False
    if cnpj in (c * LENGTH_CNPJ for c in "1234567890"):
        return False

    cnpj_base = cnpj[:12]
    digitos_verificadores = cnpj[12:]

    pesos_dv1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma_dv1 = sum(int(cnpj_base[i]) * pesos_dv1[i] for i in range(12))
    dv1 = (soma_dv1 * 10) % 11
    if dv1 >= 10:
        dv1 = 0

    cnpj_base += str(dv1)
    pesos_dv2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma_dv2 = sum(int(cnpj_base[i]) * pesos_dv2[i] for i in range(13))
    dv2 = (soma_dv2 * 10) % 11
    if dv2 >= 10:
        dv2 = 0
    return digitos_verificadores == f"{dv1}{dv2}"


def create_names(name):
    referencias = []
    created_names = True
    for nome in name:
        nome_lower = nome.lower().strip()
        try:
            obj = Names.objects.get(name=nome_lower)
            referencias.append(obj.id)
        except Names.DoesNotExist:
            test_data = {"name": nome_lower}
            serializer = CreateNames(data=test_data)
            if serializer.is_valid():
                obj = serializer.save()
                new_name = Names.objects.get(name=obj.name)
                referencias.append(new_name.id)
            else:
                created_names = False
    return created_names, referencias


def validate_username(username):
    if username is None:
        return False
    if len(username) < 3:
        return False
    if len(username) > 100:
        return False
    return True


def validate_phoneNumber(phone):
    if len(phone) != 11:
        return False

    return True


def validate_useremail(email):
    r = re.compile(r'^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')

    if r.match(email):
        return True

    return False


def validate_password(password):
    if password is None or len(password) < 8:
        return False

    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isnumeric() for char in password)

    return has_upper and has_digit


def cript_password(password):
    if not isinstance(password, str):
        raise ValueError("A senha deve ser uma string.")

    encoded_password = password.encode('utf-8')

    cripted_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
    return cripted_password.decode('utf-8')


def generate_jwt(email):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=10)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


@api_view(['POST'])
def validate_jwt(request):
    try:
        token = request.headers.get('Authorization')
        # Decodificar o token JWT
        decoded_token = jwt.decode(token,
                                   settings.SECRET_KEY, algorithms=['HS256'])

        return JsonResponse({"success": True,
                            "message": "valido"},
                            decoded_token)
    except jwt.ExpiredSignatureError:
        # O token expirou
        return JsonResponse({"success": False,
                             "message": "Token expirado"})
    except jwt.InvalidTokenError:
        # O token é inválido
        return JsonResponse({"success": False,
                             "message": "Token inválido"})


@api_view(['POST'])
def generate_new_token(request):
    email = request.data.get('email')
    if not email:
        return JsonResponse({"success": False,
                             "message": "Email is missing"},
                            status=status.HTTP_400_BAD_REQUEST)

    token = generate_jwt(email)

    return JsonResponse({"success": True,
                         "token": token},
                        status=status.HTTP_200_OK)
