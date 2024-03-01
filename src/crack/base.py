from abc import ABCMeta
from abc import abstractmethod


class Licenses(metaclass=ABCMeta):

    def gen(self):
        pass

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
                print(f"patch: \n{patch}")
        plaintext_licenses = self.parse(ciphertext_licenses)
        print(f'plaintext_licenses: \n{plaintext_licenses}')
