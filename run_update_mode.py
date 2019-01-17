"""
Copyright (c) 2019 Nitrokey UG

This file is part of nitrokey-storage-update-boot.

nitrokey-storage-update-boot is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

nitrokey-storage-update-boot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with nitrokey-storage-update-boot. If not, see <http://www.gnu.org/licenses/>.

SPDX-License-Identifier: GPL-3.0
"""

import gettext
import os
import typing
from subprocess import check_output, CalledProcessError
from time import sleep

import cffi
from progress.spinner import Spinner
from logging import getLogger, basicConfig, DEBUG, ERROR

TR_DOMAIN = 'updatevm'
LANGUAGES = {'english': 'en', 'deutsch': 'de'}
RUN_IN_DOCKER = os.path.exists('/.dockerenv')
SHUTDOWN_DELAY = 60
VERSION = '1.0'

log_print_level = ERROR
if RUN_IN_DOCKER:
    print('*** Detected Docker execution. Showing logs.')
    log_print_level = DEBUG
    SHUTDOWN_DELAY = 20

basicConfig(format='* %(relativeCreated)6d %(filename)s:%(lineno)d %(message)s',level=log_print_level)
log = getLogger().debug
ffi = cffi.FFI()
gs = ffi.string


def run_process(cmd: str):
    cmd = cmd.encode()
    try:
        out = check_output(cmd, shell=True)
        return 0, out
    except CalledProcessError as e:
        return e.returncode, e.output


translation_function : typing.Callable = None

def set_gettext(language: str, quiet: bool = False):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path_locales_abs = dir_path + '/locales'

    lang = LANGUAGES.get(language, 'en')
    gettext.bindtextdomain(TR_DOMAIN, 'locales')
    gettext.textdomain(TR_DOMAIN)
    log('path to locales: {}'.format(path_locales_abs))
    translator = gettext.translation('messages', localedir=path_locales_abs, languages=[lang])
    translator.install()
    _ = translator.gettext
    global translation_function
    translation_function = translator.gettext
    if not quiet:
        print(tr('Selected language: {} ({} {})').format(_('language').capitalize(), language.capitalize(), lang))


def set_global_lang(language: str, quiet: bool = False):
    global g_lang
    g_lang = language
    set_gettext(language, quiet)


def tr(string_to_translate: str) -> str:
    return translation_function(string_to_translate)


class DefaultPasswords:
    UPDATE = b'12345678'


class DeviceErrorCode:
    STATUS_OK = 0
    BUSY = 1  # busy or busy progressbar in place of wrong_CRC status
    NOT_PROGRAMMED = 3
    WRONG_PASSWORD = 4
    STATUS_NOT_AUTHORIZED = 5
    STATUS_AES_DEC_FAILED = 0xa
    STATUS_UNKNOWN_ERROR = 100


def C(request=None):
    import os
    original_wd = os.path.dirname(os.path.realpath(__file__))
    fp = original_wd+'/NK_C_API.h'

    declarations = []
    with open(fp, 'r') as f:
        declarations = f.readlines()

    cnt = 0
    a = iter(declarations)
    for declaration in a:
        if declaration.strip().startswith('NK_C_API'):
            declaration = declaration.replace('NK_C_API', '').strip()
            while ';' not in declaration:
                declaration += (next(a)).strip()
            # log(declaration)
            ffi.cdef(declaration, override=True)
            cnt += 1
    log('Imported {} declarations'.format(cnt))

    C = None
    import os, sys
    for path_build in [os.path.join("..", "build"), '/usr/lib/', './']:
        paths = [
            os.environ.get('LIBNK_PATH', None),
            '/root/nitrokey/libnitrokey.so',
            os.path.join(original_wd, "libnitrokey.so"),
            os.path.join('./', "libnitrokey.so"),
            os.path.join(path_build, "libnitrokey.so"),
            os.path.join(path_build, "libnitrokey.dylib"),
            os.path.join(path_build, "libnitrokey.dll"),
            os.path.join(path_build, "nitrokey.dll"),
        ]
        for p in paths:
            if not p: continue
            log("Trying " + p)
            p = os.path.abspath(p)
            if os.path.exists(p):
                log("Found: " + p)
                C = ffi.dlopen(p)
                break
            else:
                log("File does not exist: " + p)
        if not C:
            log("No library file found")
            sys.exit(1)
        else:
            break

    C.NK_set_debug_level(int(os.environ.get('LIBNK_DEBUG', 2)))



    def fin():
        log('\nFinishing connection to device')
        C.NK_logout()
        log('Finished')

    if request:
        request.addfinalizer(fin)
    # C.NK_set_debug(True)
    C.NK_set_debug_level(int(os.environ.get('LIBNK_DEBUG', 1)))

    return C


def connect_and_info(C) -> bool:
    nk_login = C.NK_login_auto()
    if nk_login != 1:
        # log('No Storage device detected. Please insert device.')
    # assert nk_login != 0  # returns 0 if not connected or wrong model or 1 when connected
        return False
    global device_type
    firmware_version = C.NK_get_minor_firmware_version()
    model = 'P' if firmware_version < 20 else 'S'
    if model == 'S':
        model = 'Nitrokey Storage'
    device_type = (model, firmware_version)
    print(tr('\nConnected device: {} 0.{}'.format(model, firmware_version)))
    return True


def run_update(C, passwords_update: bytes = DefaultPasswords.UPDATE):
    return C.NK_enable_firmware_update(passwords_update) == DeviceErrorCode.STATUS_OK


def poweroff() -> None:
    log('delay before poweroff')
    print('\n')
    print(tr('Executing system shutdown in {SHUTDOWN_DELAY} seconds.').format(SHUTDOWN_DELAY=SHUTDOWN_DELAY))
    print(tr('Once PC is powered off, please remove the USB flash drive to prevent another boot of the tool.'))

    for i in range(SHUTDOWN_DELAY):
        print('.', end='', flush=True)
        sleep(1)
    print('\n')
    print(tr('Executing system shutdown.'))
    if RUN_IN_DOCKER:
        log('Docker environment detected. Do not run poweroff.')
        return
    log('poweroff')
    run_process('poweroff')


def select_language():
    print('Select language / Sprache auswählen')
    while True:
        for i, (k,v) in enumerate(LANGUAGES.items()):
            print('{}. {} ({})'.format(i + 1, k.capitalize(), v))
        input_lang = input_protected('Language / Sprache: ')
        log('Input: {}'.format(input_lang))
        if input_lang.lower() in LANGUAGES.keys():
            break
        if input_lang.lower() in LANGUAGES.values():
            input_lang = list(LANGUAGES.values()).index(input_lang) + 1
        try:
            lang_int = int(input_lang) - 1
            log('Input lang_int (int): {}'.format(lang_int))
            if lang_int < len(LANGUAGES.keys()):
                log('In range lang_int (int): {}'.format(lang_int))
                languages_keys_ = list(LANGUAGES.keys())
                input_lang = languages_keys_[lang_int]
            break
        except:
            pass
        print('Please select again')
    set_global_lang(input_lang)


def input_protected(prompt: str) -> str:
    try:
        s = input(prompt)
        return s
    except KeyboardInterrupt:
        print()
        print(tr('CTRL+C registered. Calling system shutdown.'))
        print()
        poweroff()


if __name__ == "__main__":
    print('')
    print(f'Nitrokey Storage Update VM {VERSION}')
    # Install translator
    set_global_lang('en', quiet=True)
    select_language()

    SUCCESS_MESSAGE = tr(
        'Successfully enabled the update mode. Please run the Nitrokey Update Tool under Windows to update the firmware.')

    print(tr('This tool will activate the update mode on a Nitrokey Storage device. '
          'It is recommended for Windows 10 1809 users, where the device is not detected by the Nitrokey App, '
          'making the update mode activation not possible.'))
    print(tr('Please do not remove the flash memory stick for the time of the activation.'))
    print(tr('If you would like to exit before the device is inserted, please simply press power off switch on your '
          'computer, \nand remove the USB flash memory stick with the tool.'))
    libnitrokey = C()
    print(tr('Tool ready to work'))
    print('')
    print('')

    print(tr('Please insert Nitrokey Storage device to an empty USB slot'))
    bar = Spinner()
    try:
        while True:
            bar.next()
            if connect_and_info(libnitrokey):
                break
            sleep(0.5)
    except KeyboardInterrupt:
        bar.finish()
        poweroff()

    bar.finish()

    print(tr('Device connected. Trying default password - "{}".').format(DefaultPasswords.UPDATE.decode()))
    success = run_update(libnitrokey)

    if success:
        print(SUCCESS_MESSAGE)
        poweroff()
    else:
        print('')
        print(tr('Default firmware password has not worked.'))
        while True:
            print(tr('Please provide firmware update password, to switch the device into the update mode. '
                  '\nThe password will be displayed on the screen. This is not a PIN password. Its length is between 8 and 20 characters.'))
            user_password = input_protected(tr('Firmware password: '))
            success = run_update(libnitrokey, user_password.encode())
            if success:
                print(SUCCESS_MESSAGE)
                poweroff()
                break
            else:
                print()
                print(tr('Invalid password. Please try again.'))
