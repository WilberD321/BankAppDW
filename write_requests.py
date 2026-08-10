import os

base = r'postman\collections\BankAppDW API'

files = {}

# --- Create Customer ---
files[os.path.join(base, 'Customers', 'Create Customer.request.yaml')] = \
r"""$kind: http-request
name: Create Customer
method: POST
url: '{{baseUrl}}/api/v1/customers'
description: Creates a new customer. Returns 201 on success, 409 if customer ID already exists.
body:
  type: json
  content: |-
    {
      "id": "c003",
      "name": "Charlie",
      "email": "charlie@example.com"
    }
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status code is 201", function () {
          pm.response.to.have.status(201);
      });

      pm.test("Response has id field", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.have.property("id");
      });

      pm.test("Response has name field", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.have.property("name");
      });

      pm.test("Created customer id matches payload", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.id).to.eql("c003");
      });

      pm.test("Created customer name matches payload", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.name).to.eql("Charlie");
      });
"""

# --- Update Customer ---
files[os.path.join(base, 'Customers', 'Update Customer.request.yaml')] = \
r"""$kind: http-request
name: Update Customer
method: PUT
url: '{{baseUrl}}/api/v1/customers/{{existingCustomerId}}'
description: Updates name and/or email of an existing customer. Returns 404 if not found.
body:
  type: json
  content: |-
    {
      "name": "Alice Updated",
      "email": "alice.updated@example.com"
    }
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status code is 200", function () {
          pm.response.to.have.status(200);
      });

      pm.test("Response has id field", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.have.property("id");
      });

      pm.test("Name was updated", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.name).to.eql("Alice Updated");
      });

      pm.test("Email was updated", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.email).to.eql("alice.updated@example.com");
      });
"""

# --- Delete Customer ---
files[os.path.join(base, 'Customers', 'Delete Customer.request.yaml')] = \
r"""$kind: http-request
name: Delete Customer
method: DELETE
url: '{{baseUrl}}/api/v1/customers/{{existingCustomerId}}'
description: Deletes a customer by ID. Returns 204 on success, 404 if not found.
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status code is 204", function () {
          pm.response.to.have.status(204);
      });

      pm.test("Response body is empty", function () {
          pm.expect(pm.response.text()).to.be.empty;
      });
"""

# --- Accounts folder definition ---
files[os.path.join(base, 'Accounts', '.resources', 'definition.yaml')] = \
r"""$kind: collection
name: Accounts
description: Endpoints for managing bank accounts.
"""

# --- List Accounts ---
files[os.path.join(base, 'Accounts', 'List Accounts.request.yaml')] = \
r"""$kind: http-request
name: List Accounts
method: GET
url: '{{baseUrl}}/api/v1/accounts'
description: Returns all accounts. Supports optional query params owner_id and min_balance.
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status code is 200", function () {
          pm.response.to.have.status(200);
      });

      pm.test("Response is an array", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.be.an("array");
      });

      pm.test("Each account has id, owner_id, balance fields", function () {
          var jsonData = pm.response.json();
          jsonData.forEach(function(account) {
              pm.expect(account).to.have.property("id");
              pm.expect(account).to.have.property("owner_id");
              pm.expect(account).to.have.property("balance");
          });
      });

      pm.test("Response time is under 1000ms", function () {
          pm.expect(pm.response.responseTime).to.be.below(1000);
      });
"""

# --- Create Account ---
files[os.path.join(base, 'Accounts', 'Create Account.request.yaml')] = \
r"""$kind: http-request
name: Create Account
method: POST
url: '{{baseUrl}}/api/v1/accounts'
description: Creates a new account for an existing customer. Returns 201 on success, 409 if account ID already exists, 400 if owner not found.
body:
  type: json
  content: |-
    {
      "id": "a001",
      "owner_id": "c001",
      "balance": 500.00
    }
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status code is 201", function () {
          pm.response.to.have.status(201);
      });

      pm.test("Response has id field", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.have.property("id");
      });

      pm.test("Response has owner_id field", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.have.property("owner_id");
      });

      pm.test("Response has balance field", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.have.property("balance");
      });

      pm.test("Account id matches payload", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.id).to.eql("a001");
      });

      pm.test("Balance matches payload", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.balance).to.eql(500.00);
      });
"""

# --- Transactions folder definition ---
files[os.path.join(base, 'Transactions', '.resources', 'definition.yaml')] = \
r"""$kind: collection
name: Transactions
description: Endpoints for viewing and creating transactions.
"""

# --- List Transactions ---
files[os.path.join(base, 'Transactions', 'List Transactions.request.yaml')] = \
r"""$kind: http-request
name: List Transactions
method: GET
url: '{{baseUrl}}/api/v1/transactions'
description: Returns all transactions. Supports optional query params start_date and type.
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status code is 200", function () {
          pm.response.to.have.status(200);
      });

      pm.test("Response is an array", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.be.an("array");
      });

      pm.test("Each transaction has required fields", function () {
          var jsonData = pm.response.json();
          jsonData.forEach(function(tx) {
              pm.expect(tx).to.have.property("id");
              pm.expect(tx).to.have.property("from_account_id");
              pm.expect(tx).to.have.property("to_account_id");
              pm.expect(tx).to.have.property("amount");
              pm.expect(tx).to.have.property("type");
              pm.expect(tx).to.have.property("timestamp");
          });
      });

      pm.test("Response time is under 1000ms", function () {
          pm.expect(pm.response.responseTime).to.be.below(1000);
      });
"""

# --- Transfer ---
files[os.path.join(base, 'Transactions', 'Transfer.request.yaml')] = \
r"""$kind: http-request
name: Transfer
method: POST
url: '{{baseUrl}}/api/v1/transactions/transfer'
description: Transfers an amount between two accounts. Returns 201 with transaction details. Returns 404 if either account not found, 400 if insufficient funds.
body:
  type: json
  content: |-
    {
      "from_account_id": "a001",
      "to_account_id": "a002",
      "amount": 100.00
    }
scripts:
  - type: afterResponse
    language: text/javascript
    code: |-
      pm.test("Status code is 201", function () {
          pm.response.to.have.status(201);
      });

      pm.test("Response has transaction id", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.have.property("id");
      });

      pm.test("Transaction type is TRANSFER", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.type).to.eql("TRANSFER");
      });

      pm.test("Amount matches payload", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.amount).to.eql(100.00);
      });

      pm.test("from_account_id matches payload", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.from_account_id).to.eql("a001");
      });

      pm.test("to_account_id matches payload", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData.to_account_id).to.eql("a002");
      });

      pm.test("Response has timestamp", function () {
          var jsonData = pm.response.json();
          pm.expect(jsonData).to.have.property("timestamp");
      });
"""

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content.lstrip('\n'))
    print(f'Written: {path}')

print('All done.')
