import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

# Semente fixa para reprodutibilidade total dos dados sintéticos
SEED = 42
random.seed(SEED)

# Janela de análise: 6 meses civis completos (184 dias)
ANALYSIS_START = date(2026, 5, 1)
ANALYSIS_END = date(2026, 10, 31)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_csv(filename: str, fieldnames: list[str], rows: list[dict]) -> None:
    filepath = OUTPUT_DIR / filename
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Gerado: {filepath.name} ({len(rows)} registros)")


def generate_base_entities():
    departments = [
        {"department_id": 1, "department_name": "Operações e Manutenção"},
        {"department_id": 2, "department_name": "Engenharia de Processos"},
        {"department_id": 3, "department_name": "Qualidade e Compliance"},
        {"department_id": 4, "department_name": "Logística e Suprimentos"},
    ]

    digital_tools = [
        {
            "tool_id": 1,
            "tool_name": "Portal de Indicadores (BI)",
            "category": "Analytics & BI",
            "launch_date": "2025-11-10",
        },
        {
            "tool_id": 2,
            "tool_name": "Copilot Corporativo (IA)",
            "category": "Generative AI",
            "launch_date": "2026-07-01",
        },
        {
            "tool_id": 3,
            "tool_name": "Gestão Ágil de Tarefas (Kanban)",
            "category": "Productivity",
            "launch_date": "2026-01-15",
        },
        {
            "tool_id": 4,
            "tool_name": "Sistema de Registro Técnico",
            "category": "Operations",
            "launch_date": "2025-08-01",
        },
    ]

    first_names = [
        "Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel",
        "Helena", "Igor", "Juliana", "Lucas", "Mariana", "Nicolas", "Olivia",
        "Pedro", "Rafaela", "Samuel", "Tatiana", "Vinicius", "Yasmin",
    ]
    last_names = [
        "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira",
        "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins",
        "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa",
    ]

    dept_distribution = [1] * 32 + [2] * 26 + [3] * 22 + [4] * 20
    random.shuffle(dept_distribution)

    employees = []
    for emp_id in range(1, 101):
        full_name = f"{random.choice(first_names)} {random.choice(last_names)} {emp_id:03d}"
        dept_id = dept_distribution[emp_id - 1]

        if random.random() < 0.85:
            days_before = random.randint(30, 730)
            hire_date = ANALYSIS_START - timedelta(days=days_before)
        else:
            days_into = random.randint(1, 150)
            hire_date = ANALYSIS_START + timedelta(days=days_into)

        employees.append(
            {
                "employee_id": emp_id,
                "full_name": full_name,
                "hire_date": hire_date.isoformat(),
                "department_id": dept_id,
            }
        )

    save_csv("departments.csv", ["department_id", "department_name"], departments)
    save_csv("digital_tools.csv", ["tool_id", "tool_name", "category", "launch_date"], digital_tools)
    save_csv("employees.csv", ["employee_id", "full_name", "hire_date", "department_id"], employees)

    return departments, digital_tools, employees


def generate_tool_access(employees: list[dict], digital_tools: list[dict]) -> list[dict]:
    # Probabilidade de um funcionário receber licença por (departamento, ferramenta)
    access_probs = {
        (1, 1): 0.75, (1, 2): 0.55, (1, 3): 0.50, (1, 4): 0.95,
        (2, 1): 0.90, (2, 2): 0.85, (2, 3): 0.90, (2, 4): 0.85,
        (3, 1): 0.85, (3, 2): 0.75, (3, 3): 0.80, (3, 4): 0.90,
        (4, 1): 0.80, (4, 2): 0.65, (4, 3): 0.75, (4, 4): 0.65,
    }

    tool_access = []
    access_id = 1

    for emp in employees:
        emp_id = emp["employee_id"]
        dept_id = emp["department_id"]
        hire_dt = date.fromisoformat(emp["hire_date"])

        for tool in digital_tools:
            tool_id = tool["tool_id"]
            launch_dt = date.fromisoformat(tool["launch_date"])

            if random.random() > access_probs[(dept_id, tool_id)]:
                continue

            # O acesso nunca pode ser anterior à contratação nem ao lançamento da ferramenta
            earliest_grant = max(hire_dt, launch_dt)
            if earliest_grant > ANALYSIS_END:
                continue

            # 80% recebem acesso imediato; 20% recebem com atraso (testa elegibilidade mensal)
            if random.random() < 0.80:
                granted_dt = earliest_grant
            else:
                max_delay = (ANALYSIS_END - earliest_grant).days
                granted_dt = earliest_grant + timedelta(days=random.randint(1, min(45, max(1, max_delay))))

            # ~8% têm acesso revogado durante o período (ex: mudança de função)
            revoked_dt = None
            days_active_span = (ANALYSIS_END - granted_dt).days
            if days_active_span > 35 and random.random() < 0.08:
                revoked_dt = granted_dt + timedelta(days=random.randint(25, days_active_span - 5))

            tool_access.append(
                {
                    "access_id": access_id,
                    "employee_id": emp_id,
                    "tool_id": tool_id,
                    "access_granted_date": granted_dt.isoformat(),
                    "access_revoked_date": revoked_dt.isoformat() if revoked_dt else "",
                }
            )
            access_id += 1

    save_csv(
        "tool_access.csv",
        ["access_id", "employee_id", "tool_id", "access_granted_date", "access_revoked_date"],
        tool_access,
    )
    return tool_access


def generate_training_records(tool_access: list[dict]) -> tuple[list[dict], dict]:
    training_records = []
    training_lookup = {}
    training_id = 1

    # Janela de treinamentos entre Junho e Setembro para permitir comparação 30d antes/depois
    train_window_start = date(2026, 6, 15)
    train_window_end = date(2026, 9, 25)

    for acc in tool_access:
        # Foco de capacitação principalmente em BI (1), Copilot (2) e Kanban (3)
        if acc["tool_id"] == 4:
            invite_prob = 0.15
        else:
            invite_prob = 0.42

        if random.random() > invite_prob:
            continue

        granted_dt = date.fromisoformat(acc["access_granted_date"])
        revoked_dt = date.fromisoformat(acc["access_revoked_date"]) if acc["access_revoked_date"] else ANALYSIS_END

        earliest_train = max(train_window_start, granted_dt + timedelta(days=10))
        latest_train = min(train_window_end, revoked_dt - timedelta(days=10))

        if earliest_train >= latest_train:
            continue

        train_dt = earliest_train + timedelta(days=random.randint(0, (latest_train - earliest_train).days))
        status = "Completed" if random.random() < 0.70 else "Absent"

        training_records.append(
            {
                "training_id": training_id,
                "employee_id": acc["employee_id"],
                "tool_id": acc["tool_id"],
                "training_date": train_dt.isoformat(),
                "completion_status": status,
            }
        )
        training_lookup[(acc["employee_id"], acc["tool_id"])] = (train_dt, status)
        training_id += 1

    save_csv(
        "training_records.csv",
        ["training_id", "employee_id", "tool_id", "training_date", "completion_status"],
        training_records,
    )
    return training_records, training_lookup


def generate_usage_events(
    employees: list[dict], tool_access: list[dict], training_lookup: dict
) -> list[dict]:
    emp_dept = {emp["employee_id"]: emp["department_id"] for emp in employees}

    # Probabilidade diária base de uso em dias úteis por (departamento, ferramenta)
    base_daily_prob = {
        (1, 1): 0.18, (1, 2): 0.05, (1, 3): 0.16, (1, 4): 0.36,  # Padrão 1: Dept 1 usa pouco Copilot (tool 2)
        (2, 1): 0.32, (2, 2): 0.28, (2, 3): 0.34, (2, 4): 0.26,
        (3, 1): 0.30, (3, 2): 0.24, (3, 3): 0.28, (3, 4): 0.32,  # Padrão 2: Dept 3 tem boa frequência...
        (4, 1): 0.24, (4, 2): 0.19, (4, 3): 0.25, (4, 4): 0.22,
    }

    usage_events = []
    usage_id = 1

    for acc in tool_access:
        emp_id = acc["employee_id"]
        tool_id = acc["tool_id"]
        dept_id = emp_dept[emp_id]

        granted_dt = date.fromisoformat(acc["access_granted_date"])
        revoked_dt = date.fromisoformat(acc["access_revoked_date"]) if acc["access_revoked_date"] else ANALYSIS_END

        start_use = max(ANALYSIS_START, granted_dt)
        end_use = min(ANALYSIS_END, revoked_dt)

        if start_use > end_use:
            continue

        # Perfil individual do usuário (alguns são heavy users, outros ocasionais)
        user_affinity = random.uniform(0.55, 1.45)
        training_info = training_lookup.get((emp_id, tool_id))

        current_dt = start_use
        while current_dt <= end_use:
            # Reduz drasticamente uso em fins de semana (5 = Sábado, 6 = Domingo)
            is_weekend = current_dt.weekday() >= 5
            prob = base_daily_prob[(dept_id, tool_id)] * user_affinity

            if is_weekend:
                prob *= 0.05

            # Padrão 3: Efeito positivo após treinamento concluído (com ruído)
            post_training_boost = 1.0
            if training_info:
                train_dt, status = training_info
                if status == "Completed" and 0 < (current_dt - train_dt).days <= 45:
                    prob += 0.13
                    post_training_boost = 1.25

            if random.random() < min(prob, 0.85):
                session_count = random.randint(1, 5)

                # Padrão 2: Qualidade e Compliance (dept 3) tem sessões curtas (baixo engajamento)
                if dept_id == 3:
                    active_minutes = int(random.randint(8, 22) * post_training_boost)
                else:
                    active_minutes = int(random.randint(25, 75) * post_training_boost)

                usage_events.append(
                    {
                        "usage_id": usage_id,
                        "employee_id": emp_id,
                        "tool_id": tool_id,
                        "usage_date": current_dt.isoformat(),
                        "session_count": session_count,
                        "active_minutes": max(1, active_minutes),
                    }
                )
                usage_id += 1

            current_dt += timedelta(days=1)

    save_csv(
        "usage_events.csv",
        ["usage_id", "employee_id", "tool_id", "usage_date", "session_count", "active_minutes"],
        usage_events,
    )
    return usage_events


def generate_support_tickets(employees: list[dict], digital_tools: list[dict]) -> list[dict]:
    categories = ["Access/Permission", "Usage Question", "Error/Bug", "Integration"]
    priorities = ["Low", "Medium", "High", "Critical"]

    support_tickets = []
    ticket_id = 1

    # Gera ~210 chamados ao longo dos 6 meses
    for _ in range(210):
        emp = random.choice(employees)
        emp_id = emp["employee_id"]
        dept_id = emp["department_id"]
        hire_dt = date.fromisoformat(emp["hire_date"])

        # Padrão 1: Operações e Manutenção (dept 1) abre mais dúvidas sobre o Copilot (tool 2)
        if dept_id == 1 and random.random() < 0.45:
            tool = digital_tools[1]  # Copilot Corporativo (IA)
            category = random.choices(categories, weights=[0.15, 0.65, 0.15, 0.05])[0]
        else:
            tool = random.choice(digital_tools)
            category = random.choices(categories, weights=[0.30, 0.35, 0.20, 0.15])[0]

        tool_id = tool["tool_id"]
        launch_dt = date.fromisoformat(tool["launch_date"])

        earliest_open = max(ANALYSIS_START, hire_dt, launch_dt)
        if earliest_open > ANALYSIS_END:
            continue

        open_date = earliest_open + timedelta(days=random.randint(0, (ANALYSIS_END - earliest_open).days))
        opened_at = datetime(
            open_date.year,
            open_date.month,
            open_date.day,
            random.randint(8, 17),
            random.randint(0, 59),
            random.randint(0, 59),
        )

        priority = random.choices(priorities, weights=[0.35, 0.40, 0.18, 0.07])[0]

        # Aproximadamente 12% dos chamados permanecem em aberto (resolved_at = NULL)
        if random.random() < 0.12:
            resolved_at_str = ""
        else:
            # Tempo de resolução em horas (com alguns outliers para justificar o uso da mediana)
            if priority == "Critical":
                hours_to_resolve = random.uniform(1.0, 8.0)
            elif priority == "High":
                hours_to_resolve = random.uniform(3.0, 24.0)
            elif priority == "Medium":
                hours_to_resolve = random.uniform(6.0, 54.0)
            else:
                hours_to_resolve = random.uniform(10.0, 96.0)

            # 10% de chance de outlier demorado (ex: dependência de fornecedor/integração)
            if random.random() < 0.10:
                hours_to_resolve *= random.uniform(2.5, 4.0)

            resolved_dt = opened_at + timedelta(hours=hours_to_resolve)
            resolved_at_str = resolved_dt.strftime("%Y-%m-%d %H:%M:%S")

        support_tickets.append(
            {
                "ticket_id": ticket_id,
                "employee_id": emp_id,
                "tool_id": tool_id,
                "opened_at": opened_at.strftime("%Y-%m-%d %H:%M:%S"),
                "resolved_at": resolved_at_str,
                "category": category,
                "priority": priority,
            }
        )
        ticket_id += 1

    save_csv(
        "support_tickets.csv",
        ["ticket_id", "employee_id", "tool_id", "opened_at", "resolved_at", "category", "priority"],
        support_tickets,
    )
    return support_tickets


if __name__ == "__main__":
    departments, digital_tools, employees = generate_base_entities()
    tool_access = generate_tool_access(employees, digital_tools)
    _, training_lookup = generate_training_records(tool_access)
    generate_usage_events(employees, tool_access, training_lookup)
    generate_support_tickets(employees, digital_tools)