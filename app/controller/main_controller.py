import sys
from app.controller.delete_contact_controller import DeleteContactController
from app.view.frames.delete_contact_frame import DeleteContactFrame
from app.exceptions import ContactAlreadyExistException, ContactDoesNotExistException
from app.folder_manager import FolderManager
from app.google_contacts_wrapper_interface import GoogleContactsWrapperInterface
from app.google_sheets_wrapper_interface import GoogleSheetsWrapperInterface
# from app.view.main_window import MainWindow

from app.logger_wrapper import logger


class MainController:
    def __init__(self,
                 main_window,
                 google_sheets_wrapper: GoogleSheetsWrapperInterface,
                 google_contacts_wrapper: GoogleContactsWrapperInterface,
                 folder_manager: FolderManager
                 ):
        self.main_window = main_window
        self.google_sheets_wrapper = google_sheets_wrapper
        self.google_contacts_wrapper = google_contacts_wrapper
        self.folder_manager = folder_manager

    def create_contact(self, name: str, phone: str) -> bool:
        """creates a contact

        Args:
            name (str):
            phone (str):

        Returns:
            bool: True if successful
        """
        if not name or not phone:
            self.main_window.show_error("Please fill all the fields")
            return

        contact_dir = self.folder_manager.create_contact_folder(name)

        # Google Sheet Customer Database list: add the customer
        try:
            rows = self.google_sheets_wrapper.get_rows()
            self.google_sheets_wrapper.add_customer(rows, name)
        except BaseException as err:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            self.main_window.show_error(ex_value)
            return False

        # Google Contacts
        try:
            self.google_contacts_wrapper.create_contact_google_contacts(
                name, phone)
        except ContactAlreadyExistException as err:
            msg = err.args
            self.main_window.show_error(msg)
            logger.info(
                'ContactAlreadyExistException: skipping Google Contacts creation')
            return
        except BaseException as err:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            self.main_window.show_error(ex_value)
            return False

        # opening the directory in finder
        self.folder_manager.open_directory(contact_dir)

        self.main_window.show_info("Contact Created Successfully")
        return True

    def delete_contact(self, name: str) -> bool:
        if not name:
            self.main_window.show_error("Please fill all the fields")
            return False

        # Google Contacts Delete
        try:
            self.google_contacts_wrapper.delete_contact_google_contacts(name)
        except ContactDoesNotExistException as err:
            msg = err.args
            self.main_window.show_error(msg)
            logger.error(err)
            return False
        except BaseException as err:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            self.main_window.show_error(ex_value)
            return False

        # Delete Contact from Google Sheets
        try:
            rows = self.google_sheets_wrapper.get_rows()
            self.google_sheets_wrapper.delete_customer(rows, name)
        except ContactDoesNotExistException as err:
            msg = err.args
            self.main_window.show_error(msg)
            logger.error(err)
        except IndexError as err:
            logger.critical(err)
            raise err
        except BaseException as err:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            self.main_window.show_error(ex_value)
            return False

        # Sending it to the trash (not completely remove)
        self.folder_manager.delete_contact_folder(name)

        self.main_window.show_info("Contact Deleted Successfully")
        return True

    def switch_to_delete_frame(self):
        self.delete_contact_controller = DeleteContactController(
            self.main_window,
            self,
        )
        self.main_window.switch_view(DeleteContactFrame)
        self.main_window.container.set_controller(
            self.delete_contact_controller)

    def switch_to_create_frame(self):
        # TODO: 'should implement this. But before that do the refractor (everything inside main controller into a create_contact_frame)')
        raise NotImplemented(
            'should implement this. But before that do the refractor (everything inside main controller into a create_contact_frame)')
