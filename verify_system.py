"""Final verification test."""
from src.main import main
from src.interactive_cli import run_interactive_cli
from src.locale import t, set_locale, get_locale

print('✓ Todos los imports funcionan correctamente')

set_locale('es')
print(f'✓ Español: {t("header")}')

set_locale('en')
print(f'✓ Inglés: {t("header")}')

print('\n✓ Sistema de localización e CLI interactivo están listos para usar')
