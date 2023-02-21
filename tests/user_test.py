import pytest
from src.data import data
from src.user import user_profile_v2
from src.user import user_profile_setname_v2
from src.user import user_profile_setemail_v2
from src.user import user_profile_sethandle_v1
from src.auth import auth_register_v2
from src.auth import auth_login_v2
from src.auth import _generate_token
from src.other import clear_v1
from src.auth import auth_logout_v1
from src.validator import decode_token
import src.error as er

# Expecting pass
def test_profile():
    clear_v1()
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    token1 = auth_return1['token']
    assert({'user': {
        'u_id': 1,
        'email': 'abc123@unsw.com',
        'name_first':'First',
        'name_last': 'Last',
        'handle_str': 'firstlast0',
    }} == user_profile_v2(token1, 1))
    clear_v1()

# Expecting fail
def test_invalid_profile_uid():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_v2(token1, 5)
    clear_v1()

def test_profile_invalid_token():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    fake_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        user_profile_v2(fake_token, 0)
    clear_v1()

def test_profile_setname_invalid_token():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    fake_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        user_profile_setname_v2(fake_token, 'abc', 'def')
    clear_v1()

def test_profile_setname_short_first_name():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setname_v2(token1, '', 'Last')
    clear_v1()

def test_profile_setname_long_first_name():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setname_v2(token1, 'Abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', 'Last')
    clear_v1()

def test_profile_setname_short_last_name():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setname_v2(token1, 'First', '')
    clear_v1()

def test_profile_setname_long_last_name():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setname_v2(token1, 'First', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')
    clear_v1()

def test_profile_set_name():
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_return2 = auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    token1 = auth_return1['token']
    token2 = auth_return2['token']
    u_id2 = auth_return2['auth_user_id']
    user_profile_setname_v2(token2, 'abc', 'abc')
    assert({'user': {
        'u_id': 1,
        'email': 'abc123@unsw.com',
        'name_first':'abc',
        'name_last': 'abc',
        'handle_str': 'firstlast0',
    }} == user_profile_v2(token1, u_id2))
    clear_v1()

def test_profile_setemail_invalid_token():
    fake_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        user_profile_setemail_v2(fake_token, 'abc@gmail.com')
    clear_v1()

def test_profile_setemail_invalid_email():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_setemail_v2(token1, 'abcunsw.com')
    clear_v1()

def test_profile_setemail_already_used():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
        token1 = auth_return1['token'] 
        user_profile_setemail_v2(token1, 'abc123@unsw.com')
    clear_v1()

def test_profile_set_email():
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_return2 = auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    token1 = auth_return1['token']
    token2 = auth_return2['token']
    u_id2 = auth_return2['auth_user_id']
    user_profile_setemail_v2(token2, '123zyx@gmail.com')
    assert({'user': {
        'u_id': 1,
        'email': '123zyx@gmail.com',
        'name_first':'First',
        'name_last': 'Last',
        'handle_str': 'firstlast0',
    }} == user_profile_v2(token1, u_id2))
    clear_v1()

def test_profile_sethandle_invalid_token():
    auth_register_v2('z123456@unsw.com','123abc!@#', 'First', 'Last')
    fake_token = _generate_token(-1, -1)
    with pytest.raises(er.AccessError):
        user_profile_sethandle_v1(fake_token, 'abcdef')
    clear_v1()

def test_profile_sethandle_short_handle():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_sethandle_v1(token1, 'ab')
    clear_v1()

def test_profile_sethandle_long_handle():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        token1 = auth_return1['token'] 
        user_profile_sethandle_v1(token1, 'abcdefghijklmnopqrstuvwxyz')
    clear_v1()


def test_profile_sethandle_already_used():
    with pytest.raises(er.InputError):
        auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')   
        auth_register_v2('abc123@unsw.com', '123abc!@#', 'Firsta', 'Last')
        token1 = auth_return1['token'] 
        user_profile_sethandle_v1(token1, 'firstlast')
    clear_v1()

def test_profile_sethandle():
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_return2 = auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    token1 = auth_return1['token']
    token2 = auth_return2['token']
    auth_return2['auth_user_id']
    user_profile_sethandle_v1(token2, 'abcdef')
    assert({'user': {
        'u_id': 1,
        'email': 'abc123@unsw.com',
        'name_first':'First',
        'name_last': 'Last',
        'handle_str': 'abcdef',
    }} == user_profile_v2(token1, 1))
    clear_v1()
def test_profile_removing_email():
    auth_return1 = auth_register_v2('abc@unsw.com','123abc!@#', 'First', 'Last')
    auth_return2 = auth_register_v2('abc123@unsw.com', '123abc!@#', 'First', 'Last')
    auth_return1['token']
    token2 = auth_return2['token']
    auth_return2['auth_user_id']
    user_profile_setemail_v2(token2, '123zyx@gmail.com')
    with pytest.raises(er.InputError):
        auth_login_v2('abc123@unsw.com', '123abc!@#')
    clear_v1()