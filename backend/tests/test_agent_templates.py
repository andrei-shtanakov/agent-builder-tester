"""Tests for agent template endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.schemas import AgentTemplateCreate
from backend.app.services import agent_template_service

client = TestClient(app)


def test_create_template(db: Session) -> None:
    """Test creating a new agent template."""
    template_data = {
        "name": "Test Template",
        "description": "A test template",
        "category": "test",
        "config": {"system_message": "You are a test agent", "temperature": 0.7},
        "is_public": True,
    }

    response = client.post("/api/v1/agent-templates/", json=template_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == template_data["name"]
    assert data["description"] == template_data["description"]
    assert data["category"] == template_data["category"]
    assert data["config"] == template_data["config"]
    assert "id" in data
    assert "created_at" in data


def test_list_templates(db: Session) -> None:
    """Test listing agent templates."""
    # Create test templates
    for i in range(3):
        agent_template_service.create_template(
            db,
            AgentTemplateCreate(
                name=f"Template {i}",
                description=f"Description {i}",
                category="test",
                config={"system_message": f"Test {i}"},
                is_public=True,
            ),
        )

    response = client.get("/api/v1/agent-templates/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_get_template(db: Session) -> None:
    """Test getting a specific template."""
    # Create a template
    template_data = AgentTemplateCreate(
        name="Test Template",
        description="Test",
        category="test",
        config={"system_message": "Test"},
        is_public=True,
    )
    template = agent_template_service.create_template(db, template_data)

    response = client.get(f"/api/v1/agent-templates/{template.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(template.id)
    assert data["name"] == template.name


def test_get_template_not_found(db: Session) -> None:
    """Test getting a non-existent template."""
    import uuid

    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/agent-templates/{fake_id}")

    assert response.status_code == 404


def test_update_template(db: Session) -> None:
    """Test updating a template."""
    # Create a template
    template_data = AgentTemplateCreate(
        name="Original Name",
        description="Original",
        category="test",
        config={"system_message": "Test"},
        is_public=True,
    )
    template = agent_template_service.create_template(db, template_data)

    # Update it
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
    }

    response = client.put(f"/api/v1/agent-templates/{template.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_delete_template(db: Session) -> None:
    """Test deleting a template."""
    # Create a template
    template_data = AgentTemplateCreate(
        name="To Delete",
        description="Will be deleted",
        category="test",
        config={"system_message": "Test"},
        is_public=True,
    )
    template = agent_template_service.create_template(db, template_data)

    response = client.delete(f"/api/v1/agent-templates/{template.id}")

    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/v1/agent-templates/{template.id}")
    assert get_response.status_code == 404


def test_list_templates_by_category(db: Session) -> None:
    """Test filtering templates by category."""
    # Create templates in different categories
    categories = ["support", "development", "analytics"]
    for category in categories:
        agent_template_service.create_template(
            db,
            AgentTemplateCreate(
                name=f"Template {category}",
                description=f"Description {category}",
                category=category,
                config={"system_message": f"Test {category}"},
                is_public=True,
            ),
        )

    response = client.get("/api/v1/agent-templates/?category=support")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for template in data:
        assert template["category"] == "support"
