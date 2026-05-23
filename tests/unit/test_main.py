from unittest.mock import patch

from edit_python_pe.main import main


class TestMain:
    @patch("edit_python_pe.app.MemberApp.run")
    def test_main(self, mock_run):
        main()
        mock_run.assert_called_once()
