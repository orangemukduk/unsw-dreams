'''
datetime module for message send times
src.data imports all data
src.validator imports importal global helperfunctions
src.error import types of errors
'''
from datetime import timezone, datetime
from src.data import data
from src.validator import is_user_in_channel, is_channel_id_valid, is_user_id_valid, is_token_valid
from src.validator import is_user_channel_owner, is_message_id_valid, decode_token, is_user_in_dm
from src.validator import is_user_dm_creator, channeldm_id_from_message_id
from src.validator import is_dm_id_valid, save, load
import src.error as er
from src.other import notifications_msg


def message_send_v2(token, channel_id, message):
    '''
    MESSAGE SEND VERSION 2

    A Function that sends a message to a channel by adding all relevant information
    pertaining to the message into a list of messages for the channel
    '''
    data = load()

    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    if len(message) > 1000 or len(message) == 0:
        raise er.InputError("Message length needs to be 0 to 1000")

    if not is_channel_id_valid(channel_id):
        raise er.InputError("Channel ID not valid")

    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']

    if (not is_user_id_valid(auth_user_id)) or (
        not is_user_in_channel(auth_user_id, channel_id)):
        raise er.AccessError

    d_t = datetime.now()
    new_message = {
        'message_id': data['message_id'],
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(d_t.replace(tzinfo=timezone.utc).timestamp()),
    }    
    notifications_msg(message, auth_user_id, -1, channel_id)
    data = load()
    data['message_id'] += 1
    data['channel_list'][channel_id]['messages'].append(new_message)
    save(data)


    return {
        'message_id': new_message['message_id'],
    }



def message_remove_v1(token, message_id):
    '''
    MESSAGE REMOVE VERSION 1

    A Function to remove a message with a given ID in a channel. The remover must either be the
    message owner or an owner of the channel the message is a member of.
    '''
    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    if not is_message_id_valid(message_id):
        raise er.InputError("Invalid message ID")

    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']
    location_info = channeldm_id_from_message_id(message_id)

    if location_info['dm_id'] == -1:
        channel_id = location_info['channel_id']

        if (not is_user_id_valid(auth_user_id)) or (
            not is_user_in_channel(auth_user_id, channel_id)) or (
            not _does_user_own_message(message_id, auth_user_id)):
            raise er.AccessError("You do not have permission to send messages here")

        for message in data['channel_list'][channel_id]['messages']:
            if message['message_id'] == message_id:
                data['channel_list'][channel_id]['messages'].remove(message)

    if location_info['channel_id'] == -1:
        dm_id = location_info['dm_id']

        if (not is_user_id_valid(auth_user_id)) or (
            not is_user_in_dm(auth_user_id, dm_id)) or (
            not _does_user_own_message(message_id, auth_user_id)):
            raise er.AccessError("You do not have permission to send messages here")

        for message in data['dm_list'][dm_id]['messages']:
            if message['message_id'] == message_id:
                data['dm_list'][dm_id]['messages'].remove(message)
    
    save(data)
    return {}



def message_edit_v2(token, message_id, message):
    '''
    MESSAGE EDIT VERSION 2

    A function that edits a message. The editing user can only edit their own message and for some
    reason the owner can edit any message
    '''

    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    if len(message) > 1000 or len(message) == 0:
        raise er.InputError("Messages need to be between 0 and 1000")

    if not is_message_id_valid(message_id):
        raise er.InputError("Invalid message ID")

    location_info = channeldm_id_from_message_id(message_id)

    if location_info['dm_id'] == -1:
        channel_id = location_info['channel_id']

        token_data_struct = decode_token(token)
        auth_user_id = token_data_struct['token']['user_id']

        if (not is_user_in_channel(auth_user_id, channel_id)) or (
            not _does_user_own_message(message_id, auth_user_id)):
            raise er.AccessError("You do not have permission to edit this message")

        for message_dict in data['channel_list'][channel_id]['messages']:
            if message_dict['message_id'] == message_id:
                message_dict['message'] = message

    elif location_info['channel_id'] == -1:
        dm_id = location_info['dm_id']

        token_data_struct = decode_token(token)
        auth_user_id = token_data_struct['token']['user_id']

        if (not is_user_in_dm(auth_user_id, dm_id)) or (
            not _does_user_own_message(message_id, auth_user_id)):
            raise er.AccessError("You do not have permission to edit this message")

        for message_dict in data['dm_list'][dm_id]['messages']:
            if message_dict['message_id'] == message_id:
                message_dict['message'] = message

    save(data)
    return {}



def message_senddm_v1(token, dm_id, message):
    '''
    MESSAGE SENDDM VERSION 1

    A function to send a message to a given DM chat. This function is very similar to
    message_send but directed to a DM
    '''

    data = load()
    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    if not is_dm_id_valid(dm_id):
        raise er.InputError("DM ID is invalid")

    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']

    if (not is_user_id_valid(auth_user_id)) or (
        not is_user_in_dm(auth_user_id, dm_id)):
        raise er.AccessError("Incorrect user permissions")

    if len(message) > 1000 or len(message) == 0:
        raise er.InputError("Messages need to be between 0 and 1000")

    d_t = datetime.now()
    new_message = {
        'message_id': data['message_id'],
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(d_t.replace(tzinfo=timezone.utc).timestamp()),
    }
    notifications_msg(message, auth_user_id, dm_id, -1)
    data = load()
    data['message_id'] += 1
    data['dm_list'][dm_id]['messages'].append(new_message)

    save(data)
    
    return {
        'message_id': new_message['message_id'],
    }



def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    MESSAGE SHARE VERSION 1

    A function that allows messages to be shared through different channels. Only the message is
    shared and no other information.
    '''

    if not is_token_valid(token):
        raise er.AccessError("Invalid token")

    token_data_struct = decode_token(token)
    auth_user_id = token_data_struct['token']['user_id']
    og_message = _get_message_details(og_message_id)
    location_info = channeldm_id_from_message_id(og_message_id)

    # If the user isn't in the channel from where it is being sent from
    if location_info['dm_id'] == -1:
        if not is_user_in_channel(auth_user_id, location_info['channel_id']):
            raise er.AccessError("Incorrect permissions for user")

    # If the user idn't in the dm from where it is being sent from
    if location_info['channel_id'] == -1:
        if not is_user_in_dm(auth_user_id, location_info['dm_id']):
            raise er.AccessError("Incorrect permissions for user")

    # If the user isn't in the channel where it is being sent to
    if dm_id == -1:
        if not is_user_in_channel(auth_user_id, channel_id):
            raise er.AccessError("Incorrect permissions for user")

    # If the user idn't in the dm from where it is being sent from
    if channel_id == -1:
        if not is_user_in_dm(auth_user_id, dm_id):
            raise er.AccessError("Incorrect permissions for user")

    new_message = message + '\n\n"""\n' + og_message['message'] + '\n"""'

    if len(new_message) > 1000 or len(new_message) == 0:
        raise er.InputError("Messages must be between 0 and 1000 characters")

    if channel_id == -1:
        message_dict = message_senddm_v1(token, dm_id, new_message)

    if dm_id == -1:
        message_dict = message_send_v2(token, channel_id, new_message)

    return {
        'shared_message_id': message_dict['message_id']
    }


# Returns the dictionary containing all the information for a message
# Note this assumes correct/allowed input so security needs to be
# checked before function is called
def _get_message_details(message_id):
    data = load()
    location = channeldm_id_from_message_id(message_id)
    if location['dm_id'] == -1:
        location_id = location['channel_id']
        for message in data['channel_list'][location_id]['messages']:
            if message['message_id'] == message_id:
                return message

    if location['channel_id'] == -1:
        location_id = location['dm_id']
        for message in data['dm_list'][location_id]['messages']:
            if message['message_id'] == message_id:
                return message


# Verifies if a user owns a message OR the user is an owner of
# the channel where the message is posted
def _does_user_own_message(message_id, user_id):
    location_info = channeldm_id_from_message_id(message_id)

    if (location_info['dm_id'] == -1):
        if is_user_channel_owner(user_id, location_info['channel_id']):
            return True
            
    if location_info['channel_id'] == -1:
        if is_user_dm_creator(user_id, location_info['dm_id']):
            return True

    message_dict = _get_message_details(message_id)
    if message_dict['u_id'] == user_id:
        return True
    return False
