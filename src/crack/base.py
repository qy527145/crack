from abc import ABCMeta
from abc import abstractmethod


class KeyGen(metaclass=ABCMeta):

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def parse(self, licenses):
        pass

    @abstractmethod
    def patch(self):
        return ""

    def run(self, patch=True):
        ciphertext_licenses = self.generate()
        print(f"ciphertext_licenses: \n{ciphertext_licenses}")
        if patch:
            patch_info = self.patch()
            if patch_info:
                print(f"patch: \n{patch_info}")
        plaintext_licenses = self.parse(ciphertext_licenses)
        print(f'plaintext_licenses: \n{plaintext_licenses}')
