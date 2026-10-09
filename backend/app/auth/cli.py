import argparse
import getpass

from app.auth.store import create_user, init_auth_db, list_users, list_audit_events


def main():
    parser = argparse.ArgumentParser(description='Administração local de usuários do Oncology Management Dashboard')
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init-admin', help='Cria o primeiro administrador')
    p.add_argument('--username', required=True)
    p.add_argument('--name', required=True)
    p.add_argument('--email', default='')
    sub.add_parser('list-users')
    a = sub.add_parser('list-audit', help='Lista os eventos de auditoria mais recentes')
    a.add_argument('--limit', type=int, default=20)
    args = parser.parse_args()
    init_auth_db()
    if args.cmd == 'list-users':
        for user in list_users():
            print(f"{user['id']}\t{user['username']}\t{user['display_name']}\t{user['role']}\tativo={user['active']}\tall_convenios={user['all_convenios']}")
        return
    if args.cmd == 'list-audit':
        for row in list_audit_events(max(1, min(args.limit, 1000))):
            print(f"{row['id']}\t{row['occurred_at']}\t{row.get('actor_username') or '-'}\t{row['event_type']}\ttarget={row.get('target_user_id') or '-'}\t{row.get('remote_addr') or '-'}\t{row.get('details') or ''}")
        return
    password = getpass.getpass('Senha (mínimo 12 caracteres): ')
    confirm = getpass.getpass('Confirme a senha: ')
    if password != confirm:
        raise SystemExit('As senhas não conferem.')
    user = create_user(args.username, args.name, password, 'ADMIN', args.email, all_convenios=True)
    print(f"Administrador criado: {user['username']} ({user['display_name']})")

if __name__ == '__main__':
    main()
