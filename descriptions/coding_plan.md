# Coding Plan for Integrating Dynamic Questionnaires into the Codebase

This document outlines the steps to integrate dynamic questionnaires into the existing architecture while incorporating a standardized JSON format for dynamic form visualization and data handling. It details which parts of the code should be updated and what new files/code need to be written.

---

## 1. Overview

New functionality:
- **Admin Capabilities:** Create, update, list, and optionally delete questionnaires via a JSON schema.
- **User Capabilities:** Fetch questionnaires, fill dynamically generated forms, and submit responses.
- **Backend & Database Updates:** New tables for `questionnaires` and `form_responses`, along with corresponding models, schemas, routers, and migrations.
- **Dynamic Forms JSON Format:** Utilize a standard JSON structure for both frontend rendering and backend validation of forms.
- **Integration with Existing Auth & User Models:** Leverage current authentication and role management.

---

## 2. Database Changes

### 2.1. New Migration File
- Create an Alembic migration (e.g., `006_questionnaires.py`) to add:
  - **questionnaires table:** with columns for `questionnaire_id`, `title`, `json_schema` (JSON), `created_by`, `created_at`, and `updated_at`.
  - **form_responses table:** with columns for `response_id`, `user_id`, `questionnaire_id`, `response_data` (JSON), and `submitted_at`.
*Note:* Optionally, a `questionnaire_versions` table may be added for tracking revisions.

### 2.2. Update Existing Migrations
- Ensure consistency with existing UUID and timestamp mechanisms.

---

## 3. Backend Changes

### 3.1. New Models in `backend/app/models.py`
- Add model classes:
  - **Questionnaire** – stores the JSON schema.
  - **FormResponse** – stores user response data.
- Follow the planned signatures as described in the implementation plan.
**Planned signature examples:**

```python
class Questionnaire(Base):
    tablename = "questionnaires"
    questionnaire_id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    title = Column(String, nullable=False)
    json_schema = Column(JSON, nullable=False) # Store the JSON structure
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.uuid'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=sa.text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=sa.text("now()"), onupdate=datetime.utcnow)

class FormResponse(Base):
    tablename = "form_responses"
    response_id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid'), nullable=False)
    questionnaire_id = Column(UUID(as_uuid=True), ForeignKey('questionnaires.questionnaire_id'), nullable=False)
    response_data = Column(JSON, nullable=False)
    submitted_at = Column(DateTime, nullable=False, server_default=sa.text("now()"))
```


### 3.2. New Schemas in `backend/app/schemas.py`
- Add new Pydantic schemas:
  - **QuestionnaireCreate/Update/Response**
  - **FormResponseCreate**
**Examples:**
```python

class QuestionnaireCreate(BaseModel):
    title: str
    json_schema: dict # JSON structure for the form

class QuestionnaireUpdate(BaseModel):
    title: Optional[str]
    json_schema: Optional[dict]

class QuestionnaireResponse(BaseModel):
    questionnaire_id: str
    title: str
    json_schema: dict
    created_by: str
    created_at: datetime
    updated_at: datetime

class FormResponseCreate(BaseModel):
    user_id: str # or leave it behind the scenes from the auth middleware
    questionnaire_id: str
    response_data: dict
```

*These schemas will be used in the new router endpoints.*

### 3.3. New Routers
Create `backend/app/routers/questionnaires.py` for endpoints:
#### Admin Endpoints
- **POST /api/questionnaires** – Create a new questionnaire.
- **PUT /api/questionnaires/{id}** – Update an existing questionnaire.
- **GET /api/questionnaires** – List all questionnaires.
- **DELETE /api/questionnaires/{id}** (*Optional*) – Delete a questionnaire.

#### User Endpoints
- **GET /api/questionnaires/{id}** – Retrieve a specific questionnaire's JSON schema.
- **POST /api/form-responses** – Submit a form response.
**Key Considerations:**
- Integrate role-based authorization (only admins can create/update/delete questionnaires).
- Use middleware (like the existing authentication in `routers/auth.py`) to inject the current user.
- Validate JSON schemas on creation/update using a JSON validation library (if needed).

### 3.4. Testing
- Create new tests in `tests/test_questionnaires.py` to validate:
  - Admin creation and updating of questionnaires.
  - Retrieval of questionnaires by users.
  - Submission and storage of form responses.


---

## 4. Frontend Changes

### 4.1. Dynamic Form Renderer
- Use a library (e.g., react-jsonschema-form or a Vue equivalent) to render forms based on the JSON schema.
- Update frontend types (e.g., in `frontend/src/types/form.ts`) to represent the JSON format.

### 4.2. New JSON Format Integration
- **Standard JSON Schema for Forms:**  
  Incorporate the following structure, which defines:
  - `title`, `description`
  - `fields`: an array where each object specifies:
    - `id`, `type` (text, email, number, date, select, radio, checkbox, textarea)
    - `label`, `placeholder`, `required`
    - `options` for select/radio types, and `default` values if needed.
- Example JSON snippet should be referenced in the code documentation and type definitions.

### 4.3. Frontend-Bot & Backend Interaction
- Ensure the JSON schema is fetched from `/api/questionnaires/{id}`.
- On form submission, the frontend sends a JSON object with field IDs and values to `/api/form-responses`.
  
---

## 5. Step-by-Step Implementation Process

1. **Migration:**
   - Write a migration in `backend/migrations/versions/003_questionnaires.py`.
   - Apply migration to create new tables.
2. **Backend Model & Schema Updates:**
   - Update `models.py` and `schemas.py` with Questionnaire and FormResponse models.
3. **New Router Implementation:**
   - Create `routers/questionnaires.py` with endpoints for admin and user operations.
4. **Frontend Integration:**
   - Update dynamic form renderer to use the standard JSON schema.
   - Create or update type definitions for the JSON schema in `frontend/src/types/`.
5. **Testing:**
   - Write tests in `tests/test_questionnaires.py` to cover admin creation, schema retrieval, dynamic rendering, and form response submission.
6. **Documentation Update:**
   - Update `backend/README.md` and frontend documentation to mention the JSON format and new endpoints.
7. **End-to-End Integration Testing:**
   - Validate the full workflow from form building to submission and storage.

---

## 6. Additional Frontend Considerations (Update)

- **New JSON Format Integration:**  
  - Adopt the standardized dynamic form JSON schema as defined in the updated implementation plan.
  - Ensure the frontend renders components (text input, email input, number input, select dropdown, radio buttons, checkbox) correctly based on the JSON properties.
  - Update the state management (e.g., Vuex or Redux) to include the dynamic form state.

- **Type Definitions:**  
  - Create or update types (e.g., in `frontend/src/types/form.ts`) to provide clear structure definitions for the dynamic form JSON.

---

## 7. Summary & Next Steps

- **Updated Files:**
  - `backend/app/models.py`: Add new models.
  - `backend/app/schemas.py`: Add new JSON-related schemas.
  - `backend/migrations/versions/006_questionnaires.py`: New migration.
  - `backend/app/routers/questionnaires.py`: New router for handling questionnaires.
  - `frontend/src/types/form.ts` (or similar): New type definitions for dynamic form JSON.
- **New Files:**
  - `tests/test_questionnaires.py`: Tests for new endpoints.
- **Unchanged Code:**
  - Existing authentication and user management modules remain unchanged but are reused for authorization checks.
  
By following this coding plan and adopting the standardized JSON format for dynamic forms, admins will be able to create visually appealing, dynamic questionnaires, and users will have a smooth experience filling and submitting form data.

--- 

## 1. Role Selection Implementation

### UI Component (RoleSelector.vue)
```vue
<template>
  <v-card>
    <v-card-title>Select Your Roles</v-card-title>
    <v-card-text>
      <v-checkbox
        v-for="role in availableRoles"
        v-model="selectedRoles"
        :key="role.id"
        :label="role.label"
        :value="role.id"
      />
    </v-card-text>
    <v-card-actions>
      <v-btn @click="saveRoles" :loading="isSaving">
        Save Roles
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
```

### TypeScript Interfaces
```typescript
// types/role.ts
interface Role {
  id: 'entrepreneur' | 'investor' | 'researcher';
  label: string;
}

interface UserRoles {
  userId: string;
  roles: Role[];
}
```

### Python Models/Schemas
```python
# schemas.py
class RoleCreate(BaseModel):
    role: str

class UserRoleResponse(BaseModel):
    user_id: UUID
    role: str
    created_at: datetime

# models.py (existing)
class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 2. Questionnaire System

### UI Components

#### QuestionnaireBuilder.vue (Admin)
```vue
<template>
  <v-form v-model="isValid">
    <v-text-field
      v-model="form.title"
      label="Title"
      :rules="[rules.required]"
    />
    <v-select
      v-model="form.role"
      :items="availableRoles"
      label="Role"
      :rules="[rules.required]"
    />
    <DynamicFieldBuilder
      v-model="form.fields"
      @update:fields="updateFields"
    />
  </v-form>
</template>
```

#### QuestionnaireForm.vue (User)
```vue
<template>
  <v-form v-model="isValid">
    <template v-for="field in questionnaire.fields">
      <v-text-field
        v-if="field.type === 'text'"
        v-model="answers[field.id]"
        :label="field.label"
        :rules="getFieldRules(field)"
      />
      <!-- Other field types... -->
    </template>
  </v-form>
</template>
```

### Data Structures

#### TypeScript Types
```typescript
// types/questionnaire.ts
interface QuestionnaireField {
  id: string;
  type: 'text' | 'email' | 'number' | 'date' | 'select' | 'radio' | 'checkbox' | 'textarea';
  label: string;
  placeholder?: string;
  required: boolean;
  options?: string[];
}

interface Questionnaire {
  id: string;
  title: string;
  description?: string;
  role: string;
  fields: QuestionnaireField[];
}

interface QuestionnaireResponse {
  id: string;
  questionnaire_id: string;
  user_id: string;
  answers: Record<string, any>;
  submitted_at: string;
}
```

#### Python Models
```python
# models.py
class QuestionnaireDB(Base):
    __tablename__ = "questionnaires"
    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    role = Column(String, nullable=False)
    fields = Column(JSONB, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))
    created_at = Column(DateTime, server_default=text('now()'))

class QuestionnaireResponseDB(Base):
    __tablename__ = "questionnaire_responses"
    id = Column(UUID(as_uuid=True), primary_key=True)
    questionnaire_id = Column(UUID(as_uuid=True), ForeignKey('questionnaires.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))
    answers = Column(JSONB, nullable=False)
    submitted_at = Column(DateTime, server_default=text('now()'))
```

## 3. Implementation Steps

### 1. Database Migration
```python
# migrations/versions/006_questionnaires.py
def upgrade():
    # Create questionnaires table
    op.create_table(
        'questionnaires',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('fields', JSONB, nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.uuid')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
```

### 2. API Endpoints
```python
@router.post("/roles", response_model=List[UserRoleResponse])
async def add_user_roles(
    roles: List[RoleCreate],
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
)

@router.get("/questionnaires/by-role/{role}", response_model=List[QuestionnaireResponse])
async def get_questionnaires_by_role(
    role: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
)
```

### 3. Frontend Store
```typescript
// stores/questionnaire.ts
interface QuestionnaireState {
  questionnaires: Record<string, Questionnaire[]>;  // Indexed by role
  currentResponses: Record<string, any>;
  isLoading: boolean;
  error: string | null;
}

export const $questionnaireStore = createStore<QuestionnaireState>({
  questionnaires: {},
  currentResponses: {},
  isLoading: false,
  error: null
});

export const fetchQuestionnairesByRoleFx = createEffect(async (role: string) => {
  const response = await api.get(`/api/questionnaires/by-role/${role}`);
  return response.data;
});
```

## 4. Testing Strategy

### Backend Tests
```python
def test_add_user_roles():
    # Test adding multiple roles to user
    
def test_get_questionnaires_by_role():
    # Test retrieving role-specific questionnaires

def test_submit_questionnaire_response():
    # Test response submission and validation
```

### Frontend Tests
```typescript
describe('RoleSelector', () => {
  it('allows multiple role selection', () => {
    // Test multiple role selection
  });
  
  it('loads appropriate questionnaires after role selection', () => {
    // Test questionnaire loading
  });
});
``` 