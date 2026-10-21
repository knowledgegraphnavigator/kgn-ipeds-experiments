# Verification: Rose-Hulman Institute of Technology (UNITID 152318)

Reference graph: 66 triples built directly from the data model.

| Format | File | Triples | Identical graph | Same facts* |
|---|---|---|---|---|
| JSON-LD | `institution.jsonld` | 66 | yes | yes |
| Microdata | `institution.microdata.html` | 66 | no | yes |
| RDFa | `institution.rdfa.html` | 67 | no | yes |
| Turtle | `institution.ttl` | 66 | yes | yes |
| N-Triples | `institution.nt` | 66 | yes | yes |
| JSONL | `institutions.jsonl` | 66 | yes | yes |

*Same facts: literals compared by lexical value only (datatypes and language tags ignored), and parser bookkeeping triples such as `rdfa:usesVocabulary` dropped.

## Microdata: what changed

- **string -> string@en** on 37 triples (e.g. alternateName: R-HIT; alternateName: RHIT; alternateName: RP; ...)
- **xsd:decimal -> xsd:double** on 4 triples (e.g. value: 76.9; latitude: 39.483602; longitude: -87.326749; ...)

## RDFa: what changed

- **string -> string@en** on 37 triples (e.g. alternateName: R-HIT; alternateName: RHIT; alternateName: RP; ...)
- **extra triple** added by the parser: usesVocabulary: https://schema.org/
