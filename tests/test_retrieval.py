from src.retrieval import find_vehicles, search_corpus


def test_structured_vehicle_lookup():
    found = find_vehicles("Volkswagen", "Polo", 2018, "TSI")
    assert len(found) == 1
    assert found[0]["cambio"] == "Automático de 6 velocidades"


def test_text_retrieval_prefers_current_document():
    found = search_corpus("precisa de aprovação para registrar interesse?")
    assert found
    assert found[0].current is True
    assert "operador" in found[0].excerpt.lower()


def test_revoked_document_is_present_but_marked():
    found = search_corpus("registro direto sem revisão", top_k=10)
    assert any(not source.current for source in found)

