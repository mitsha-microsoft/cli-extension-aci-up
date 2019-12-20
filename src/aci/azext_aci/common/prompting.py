import sys
from knack.log import get_logger
from knack.prompting import prompt, verify_is_a_tty, NoTTYException

logger = get_logger(__name__)

def delete_last_line():
    from colorama import init, deinit
    init()
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[2K')
    deinit()

def prompt_user_friendly_choice_list(msg, a_list, default=1, help_string=None, error_msg=None):
    verify_is_a_tty_or_raise_error(error_msg=error_msg)
    options = '\n'.join([' [{}] {}{}'.format(i+1, x['name'] if isinstance(x, dict) and 'name' in x else x, ' - ' + x['desc'] if isinstance(x, dict) and 'desc' in x else '') for i,x in enumerate(a_list)])
    #TODO: This option is just for show and doesnt actually work
    options += '\n [{}] Create a new Azure Container Registry'.format(len(a_list)+1)
    allowed_vals = list(range(1, len(a_list) + 2))
    linesToDelete = len(a_list) + 2
    while True:
        val = prompt('{}\n{}\nPlease enter a choice [Default Choice({})]: '.format(msg, options, default))
        if val == '?' and help_string is not None:
            for x in range(0, linesToDelete):
                delete_last_line()
            print('Please enter a choice [Default choice({})]: {}'.format(default, '?'))
            print(help_string)
            continue
        if not val:
            val = '{}'.format(default)
        try:
            ans = int(val)
            if ans in allowed_vals:
                for x in range(0, linesToDelete):
                    delete_last_line()
                #TODO: Doubtful. May need to remove these print statements
                #TODO: Cant select the new acr list option right now!
                print('Please enter a choice [Default choice({})]: {}'.format(default, a_list[ans - 1]))
                print('')
                return ans - 1
            raise ValueError
        except ValueError:
            for x in range(0, linesToDelete):
                    delete_last_line()
            print('Please enter a choice [Default choice({})]: {}'.format(default, val))
            logger.warning('Valid values are %s',allowed_vals)

def verify_is_a_tty_or_raise_error(error_msg=None):
    try:
        verify_is_a_tty()
    except NoTTYException:
        raise NoTTYException(error_msg)