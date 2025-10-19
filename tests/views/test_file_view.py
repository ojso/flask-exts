from io import BytesIO
import os
import os.path as op

from flask_exts.views.file.local_file_view import LocalFileView


class FileViewTests:
    _test_files_root = op.join(op.dirname(__file__), "files")

    def fileadmin_class(self):
        raise NotImplementedError

    def fileadmin_args(self):
        raise NotImplementedError

    def test_file_admin(self, client, admin):
        fileadmin_class = self.fileadmin_class()
        fileadmin_args, fileadmin_kwargs = self.fileadmin_args()
        # print(fileadmin_args)

        class MyFileAdmin(fileadmin_class):
            editable_extensions = ("txt",)

        view_kwargs = dict(fileadmin_kwargs)
        view_kwargs.setdefault("name", "Files")
        view = MyFileAdmin(*fileadmin_args, **view_kwargs)
        admin.add_view(view)

        # index
        rv = client.get("/admin/myfileadmin/")
        assert rv.status_code == 200
        assert "path=dummy.txt" in rv.text

        # edit
        rv = client.get("/admin/myfileadmin/edit/?path=dummy.txt")
        assert rv.status_code == 200
        assert "dummy.txt" in rv.text

        rv = client.post(
            "/admin/myfileadmin/edit/?path=dummy.txt",
            data=dict(content="new_string"),
        )
        assert rv.status_code == 302

        rv = client.get("/admin/myfileadmin/edit/?path=dummy.txt")
        assert rv.status_code == 200
        assert "dummy.txt" in rv.text
        assert "new_string" in rv.text

        # rename
        rv = client.get("/admin/myfileadmin/rename/?path=dummy.txt")
        assert rv.status_code == 200
        assert "dummy.txt" in rv.text

        rv = client.post(
            "/admin/myfileadmin/rename/?path=dummy.txt",
            data=dict(name="dummy_renamed.txt", path="dummy.txt"),
        )
        assert rv.status_code == 302

        rv = client.get("/admin/myfileadmin/")
        assert rv.status_code == 200
        assert "path=dummy_renamed.txt" in rv.text
        assert "path=dummy.txt" not in rv.text

        # upload
        rv = client.get("/admin/myfileadmin/upload/")
        assert rv.status_code == 200

        rv = client.post(
            "/admin/myfileadmin/upload/",
            data=dict(upload=(BytesIO(b""), "dummy.txt")),
        )
        assert rv.status_code == 302

        rv = client.get("/admin/myfileadmin/")
        assert rv.status_code == 200
        assert "path=dummy.txt" in rv.text
        assert "path=dummy_renamed.txt" in rv.text

        # delete
        rv = client.post(
            "/admin/myfileadmin/delete/", data=dict(path="dummy_renamed.txt")
        )
        assert rv.status_code == 302

        rv = client.get("/admin/myfileadmin/")
        assert rv.status_code == 200
        assert "path=dummy_renamed.txt" not in rv.text
        assert "path=dummy.txt" in rv.text

        # mkdir
        rv = client.get("/admin/myfileadmin/mkdir/")
        assert rv.status_code == 200

        rv = client.post("/admin/myfileadmin/mkdir/", data=dict(name="dummy_dir"))
        assert rv.status_code == 302

        rv = client.get("/admin/myfileadmin/")
        assert rv.status_code == 200
        assert "path=dummy.txt" in rv.text
        assert "path=dummy_dir" in rv.text

        # rename - directory
        rv = client.get("/admin/myfileadmin/rename/?path=dummy_dir")
        assert rv.status_code == 200
        assert "dummy_dir" in rv.text

        rv = client.post(
            "/admin/myfileadmin/rename/?path=dummy_dir",
            data=dict(name="dummy_renamed_dir", path="dummy_dir"),
        )
        assert rv.status_code == 302

        rv = client.get("/admin/myfileadmin/")
        assert rv.status_code == 200
        assert "path=dummy_renamed_dir" in rv.text
        assert "path=dummy_dir" not in rv.text

        # delete - directory
        rv = client.post(
            "/admin/myfileadmin/delete/", data=dict(path="dummy_renamed_dir")
        )
        assert rv.status_code == 302

        rv = client.get("/admin/myfileadmin/")
        assert rv.status_code == 200
        assert "path=dummy_renamed_dir" not in rv.text
        assert "path=dummy.txt" in rv.text

    def test_modal_edit(self, client, admin):
        fileadmin_class = self.fileadmin_class()
        fileadmin_args, fileadmin_kwargs = self.fileadmin_args()

        class EditModalOn(fileadmin_class):
            edit_modal = True
            editable_extensions = ("txt",)

        class EditModalOff(fileadmin_class):
            edit_modal = False
            editable_extensions = ("txt",)

        on_view_kwargs = dict(fileadmin_kwargs)
        on_view_kwargs.setdefault("endpoint", "edit_modal_on")
        edit_modal_on = EditModalOn(*fileadmin_args, **on_view_kwargs)

        off_view_kwargs = dict(fileadmin_kwargs)
        off_view_kwargs.setdefault("endpoint", "edit_modal_off")
        edit_modal_off = EditModalOff(*fileadmin_args, **off_view_kwargs)

        admin.add_view(edit_modal_on)
        admin.add_view(edit_modal_off)

        # bootstrap 3 - ensure modal window is added when edit_modal is
        # enabled
        rv = client.get("/admin/edit_modal_on/")
        assert rv.status_code == 200
        assert "fa_modal_window" in rv.text

        # bootstrap 3 - test modal disabled
        rv = client.get("/admin/edit_modal_off/")
        assert rv.status_code == 200
        assert "fa_modal_window" not in rv.text


class TestLocalFileAdmin(FileViewTests):
    def fileadmin_class(self):
        return LocalFileView

    def fileadmin_args(self):
        return (self._test_files_root,), {}

    def test_fileadmin_sort_url_param(self, client, admin):
        fileadmin_class = self.fileadmin_class()
        fileadmin_args, fileadmin_kwargs = self.fileadmin_args()

        class MyFileAdmin(fileadmin_class):
            editable_extensions = ("txt",)

        view_kwargs = dict(fileadmin_kwargs)
        view_kwargs.setdefault("name", "Files")
        view = MyFileAdmin(*fileadmin_args, **view_kwargs)

        admin.add_view(view)

        with open(op.join(self._test_files_root, "dummy2.txt"), "w") as fp:
            # make sure that 'files/dummy2.txt' exists, is newest and has bigger size
            fp.write("test")

            rv = client.get("/admin/myfileadmin/")
            assert rv.status_code == 200
            pos1 = rv.text.find("path=dummy.txt")
            pos2 = rv.text.find("path=dummy2.txt")
            assert pos1 > 0
            assert pos2 > 0
            assert pos1 < pos2

            rv = client.get("/admin/myfileadmin/?sort=name")
            assert rv.status_code == 200
            pos1 = rv.text.find("path=dummy.txt")
            pos2 = rv.text.find("path=dummy2.txt")
            assert pos1 > 0
            assert pos2 > 0
            assert pos1 < pos2

            rv = client.get("/admin/myfileadmin/?sort=date&desc=1")
            assert rv.status_code == 200
            pos1 = rv.text.find("path=dummy.txt")
            pos2 = rv.text.find("path=dummy2.txt")
            assert pos1 > 0
            assert pos2 > 0
            assert pos1 > pos2

        try:
            # clean up
            os.remove(op.join(self._test_files_root, "dummy2.txt"))
        except (IOError, OSError):
            pass
