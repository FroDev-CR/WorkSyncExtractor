"""
Queries y mutations GraphQL de Jobber como constantes.
Validadas contra la API version 2025-01-20.
"""

# ── Clients ───────────────────────────────────────────────────────────────────

LIST_CLIENTS_QUERY = """
query ListClients {
  clients(first: 100) {
    nodes {
      id
      name
      companyName
      isCompany
    }
  }
}
"""

CREATE_CLIENT_MUTATION = """
mutation ClientCreate($input: ClientCreateInput!) {
  clientCreate(input: $input) {
    client {
      id
      name
      companyName
    }
    userErrors {
      message
      path
    }
  }
}
"""

# ── Properties ────────────────────────────────────────────────────────────────

FIND_PROPERTY_QUERY = """
query FindProperty($clientId: EncodedId!) {
  client(id: $clientId) {
    clientProperties(first: 100) {
      nodes {
        id
        address {
          street1
          street2
          city
          province
          postalCode
          country
        }
      }
    }
  }
}
"""

CREATE_PROPERTY_MUTATION = """
mutation PropertyCreate($clientId: EncodedId!, $address: PropertyAddressInput!) {
  propertyCreate(clientId: $clientId, address: $address) {
    property {
      id
      address {
        street1
        city
      }
    }
    userErrors {
      message
      path
    }
  }
}
"""

# ── Jobs ──────────────────────────────────────────────────────────────────────

CREATE_JOB_MUTATION = """
mutation JobCreate($attributes: JobCreateAttributes!) {
  jobCreate(attributes: $attributes) {
    job {
      id
      jobNumber
      jobberWebUri
    }
    userErrors {
      message
      path
    }
  }
}
"""

# ── Account ───────────────────────────────────────────────────────────────────

ACCOUNT_QUERY = """
query {
  account {
    id
    name
  }
}
"""
