# Log błędu Allplan — materiał ściany 240 mm

- Data: 2026-10-24
- Operacja: zmiana natywnego materiału ściany o grubości 240 mm na `Silikat`
- Wynik: bez zapisu; podgląd planu został zablokowany.

## Użyte narzędzia MCP

### 1. `mcp__allplan_m0__model_query`

Wywołanie:

```json
{
  "request": {
    "action": "query",
    "component_kind": "semantic_component",
    "fields": [
      "display_name",
      "type_name",
      "type_uuid",
      "drawing_file",
      "wall.total_thickness_mm"
    ],
    "predicate": {
      "field": "wall.total_thickness_mm",
      "op": "eq",
      "value": 240
    },
    "page_size": 20
  }
}
```

Istotny wynik odczytu:

- `scan_complete`: `true`
- `requested_scope_complete`: `false`
- aktywny rysunek: `101`
- znaleziony element: `Ściana, prosta`
- `type_name`: `Wall_TypeUUID`
- `wall.total_thickness_mm`: `240.0`
- `model_uuid`: `06d71e4d-193b-483e-8a32-344ade3d612c`
- `usable_for_write`: `false`
- `request_id`: `f5fc110f-ad9f-481a-a5fd-70326103c27a`

### 2. `mcp__allplan_m0__model_edit`

Wywołanie podglądu (bez zapisu):

```json
{
  "request": {
    "action": "preview",
    "scope": "open_drawings",
    "native_types": ["Wall_TypeUUID"],
    "predicate": {
      "field": "wall.total_thickness_mm",
      "op": "eq",
      "value": 240
    },
    "changes": [
      {
        "target": {
          "kind": "native_material",
          "tier_index": 1
        },
        "value": "Silikat"
      }
    ]
  }
}
```

Dokładny błąd / blokada zwrócone w wyniku:

```json
{
  "field": "wall.native_material",
  "reason": "native_material_preservation_unavailable",
  "old_value": {
    "status": "observed",
    "value": "Beton"
  },
  "observation": {
    "status": "not_checked",
    "value": null,
    "reason": "wall_material_tier_child_unsupported",
    "diagnostic": {
      "stage": "material_tier_children",
      "error_type": "ValueError",
      "evidence": {
        "owner": {
          "drawing_file": 101,
          "signed_drawing_file": 101,
          "model_uuid": "4db19151-9090-4b1c-bd50-b6fba6873aff",
          "view_uuid": "6e5cd6d9-31de-437c-95c1-a20bda7da3d0",
          "type_name": "WallTier_TypeUUID",
          "type_uuid": "a7fae808-845c-4491-9f44-3757c493e673"
        },
        "child": {
          "drawing_file": 101,
          "signed_drawing_file": 101,
          "model_uuid": "6446ff90-420c-4d1d-8d3f-cccb1987c768",
          "view_uuid": "f8677785-5357-4c56-883b-6002f443367c",
          "type_name": "WallAxis_TypeUUID",
          "type_uuid": "b7b85ac6-3b03-4b81-a353-153216f8ae4d"
        }
      }
    }
  }
}
```

Dodatkowe pola wyniku podglądu:

- `request_id`: `c5e0d95e-f705-44d4-b903-f12b2f0732a2`
- `plan_id`: `7cb19ce69f1242229b441a289e71424c`
- `plan_hash`: `adece99dd84670cf267ba10cc7328f0d2f22b3c77b6f6ff80d968c6f3be0a1d2`
- `counts`: `matched=1`, `blocked=1`, `changes=0`
- `usable_for_write`: `false`
- `write_blockers`: `not_checked`, `blocked_properties`
- `setter_calls_started`: `0`
- `apply_available`: `false`
- `production_apply_available`: `false`

Uwaga: odpowiedź narzędzia podała typ wyjątku `ValueError`, ale nie zawierała tekstowego pola z komunikatem wyjątku (`message`). Nie dopisano ani nie zgadywano takiego komunikatu.
