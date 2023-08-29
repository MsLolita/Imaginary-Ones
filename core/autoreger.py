import time
from concurrent.futures import ThreadPoolExecutor

from core.utils import shift_file, logger
from core.utils.auto_generate.emails import generate_random_emails
from core.utils.auto_generate.wallets import generate_random_wallets
from core.utils.file_to_list import file_to_list
from core.imaginaryones import ImaginaryOnes

from inputs.config import (
    THREADS, CUSTOM_DELAY,
    EMAILS_FILE_PATH, WALLETS_FILE_PATH, DISCORDS_FILE_PATH, PROXIES_FILE_PATH, REFERRAL_CODES_PATH
)


class AutoReger:
    def __init__(self):
        self.success = 0
        self.custom_user_delay = None
        self.ref_links = None

    @staticmethod
    def get_accounts():
        emails = file_to_list(EMAILS_FILE_PATH)
        wallets = file_to_list(WALLETS_FILE_PATH)
        discords = file_to_list(DISCORDS_FILE_PATH)
        proxies = file_to_list(PROXIES_FILE_PATH)

        discords.reverse()

        temp_ds = []
        for discord in discords:
            temp_ds.append(next(item for item in discord.split(":") if len(item) > 50))

        discords = temp_ds

        min_accounts_len = len(discords)

        if not emails:
            logger.info(f"Generated random emails!")
            emails = generate_random_emails(min_accounts_len)

        if not wallets:
            logger.info(f"Generated random wallets!")
            wallets = [wallet[0] for wallet in generate_random_wallets(min_accounts_len)]

        accounts = []

        for i in range(min_accounts_len):
            accounts.append((emails[i], wallets[i], discords[i], proxies[i] if len(proxies) > i else None))

        return accounts

    @staticmethod
    def remove_account():
        return (shift_file(EMAILS_FILE_PATH), shift_file(WALLETS_FILE_PATH),
                shift_file(DISCORDS_FILE_PATH), shift_file(PROXIES_FILE_PATH), shift_file(REFERRAL_CODES_PATH))

    def start(self):
        self.ref_links = file_to_list("inputs/referral_codes.txt")
        self.ref_links.sort()

        if not self.ref_links:
            logger.info("referral_codes.txt is empty")
            return

        threads = THREADS

        self.custom_user_delay = CUSTOM_DELAY

        accounts = AutoReger.get_accounts()

        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.register, accounts)

        if self.success:
            logger.success(f"Successfully registered {self.success} accounts :)")
        else:
            logger.warning(f"No accounts registered :(")

    def register(self, account: tuple):
        imaginary_ones = ImaginaryOnes(*account, ref_code=self.ref_links.pop())
        is_ok = False

        try:
            time.sleep(self.custom_user_delay)

            imaginary_ones.register()
            imaginary_ones.connect_ds()
            is_ok = imaginary_ones.claim_chest()

            # is_ok = imaginary_ones.verify_email()
        except Exception as e:
            logger.error(f"Error {e}")

        AutoReger.remove_account()

        if is_ok:
            imaginary_ones.logs()
            self.success += 1
        else:
            imaginary_ones.logs_fail()

    @staticmethod
    def is_file_empty(path: str):
        return not open(path).read().strip()
