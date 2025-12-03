"""
FLEURDIN AI - CHUNKING STRATEGY IMPLEMENTATION
==============================================
Implementace hybridní chunking strategie (entity-based + fixed-size)

Parametry (optimalizováno pro GPT-4-mini):
- Entity-based: <1,500 znaků = celé, <2,500 znaků = celé
- Fixed-size: 1,200 znaků, 200 overlap (17%)
- Embedding model: paraphrase-multilingual-MiniLM-L12-v2
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
import re


class ChunkingStrategy:
    """Implementace hybridní chunking strategie"""

    def __init__(self):
        # Chunking parametry (optimalizováno pro GPT-4-mini + náklady)
        self.config = {
            "entity_based": {
                "small_entity_max": 1500,      # Malé entity - ponechat celé
                "medium_entity_max": 2500      # Střední entity - ponechat celé
            },
            "fixed_size": {
                "chunk_size": 1200,            # KOMPROMIS pro náklady + kvalitu
                "overlap": 200                 # 17% overlap
            },
            "heading_detection": {
                "max_length": 100,             # Max délka nadpisu
                "keywords": [
                    "Kapitola", "kapitola",
                    "Úvod", "úvod",
                    "Prečo", "Ako", "Čo",
                    "?", ":"
                ]
            }
        }

    def chunk_all_data(self, parsed_data_path: str) -> Dict:
        """Aplikuje chunking strategii na všechna data"""

        print("\n" + "="*70)
        print("🧩 CHUNKING STRATEGY - APLIKACE")
        print("="*70)
        print(f"\nParametry:")
        print(f"  • Malé entity: <{self.config['entity_based']['small_entity_max']} znaků")
        print(f"  • Střední entity: <{self.config['entity_based']['medium_entity_max']} znaků")
        print(f"  • Fixed-size: {self.config['fixed_size']['chunk_size']} znaků")
        print(f"  • Overlap: {self.config['fixed_size']['overlap']} znaků")

        # Load parsed data
        with open(parsed_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Výstupní struktura
        chunked_data = {
            "essential_oils": [],
            "herbs_books": [],
            "voice_transcripts": [],
            "stats": {}
        }

        # 1. ESENCIÁLNÍ OLEJE - již jsou optimální chunky
        print("\n" + "-"*70)
        print("1️⃣  ESENCIÁLNÍ OLEJE")
        oils = [c for c in data['chunks'] if c['type'] == 'essential_oil']
        chunked_data["essential_oils"] = self._chunk_essential_oils(oils)

        # 2. KNIHY O BYLINKÁCH - detekce entit + hybridní chunking
        print("\n" + "-"*70)
        print("2️⃣  KNIHY O BYLINKÁCH")
        book1_paras = [c for c in data['chunks'] if c['type'] == 'herb_book' and 'book1' in c['id']]
        book2_paras = [c for c in data['chunks'] if c['type'] == 'herb_book' and 'book2' in c['id']]

        chunked_data["herbs_books"].extend(self._chunk_book(book1_paras, "book1"))
        chunked_data["herbs_books"].extend(self._chunk_book(book2_paras, "book2"))

        # 3. VOICE TRANSKRIPTY - fixed-size chunking
        print("\n" + "-"*70)
        print("3️⃣  VOICE TRANSKRIPTY")
        transcripts = [c for c in data['chunks'] if c['type'] == 'transcript']
        chunked_data["voice_transcripts"] = self._chunk_voice_transcripts(transcripts)

        # Stats
        chunked_data["stats"] = {
            "essential_oils": len(chunked_data["essential_oils"]),
            "herbs_books": len(chunked_data["herbs_books"]),
            "voice_transcripts": len(chunked_data["voice_transcripts"]),
            "total": (
                len(chunked_data["essential_oils"]) +
                len(chunked_data["herbs_books"]) +
                len(chunked_data["voice_transcripts"])
            )
        }

        return chunked_data

    def _chunk_essential_oils(self, oils: List[Dict]) -> List[Dict]:
        """
        Esenciální oleje - ponechat jako celé chunky
        Jsou již optimální (~1,000-1,500 znaků)
        """
        print(f"  • Zpracovávám {len(oils)} olejů...")

        chunked_oils = []
        for oil in oils:
            size = len(oil['text'])

            # Přidat metadata pro RAG
            chunk = {
                "id": oil['id'],
                "type": "essential_oil",
                "entity_name": oil['name'],
                "entity_type": "essential_oil",
                "text": oil['text'],
                "part": 1,
                "total_parts": 1,
                "tier": "free",  # Default - upravíš podle potřeby
                "metadata": {
                    **oil['metadata'],
                    "english_name": oil.get('english_name', ''),
                    "latin_name": oil.get('latin_name', ''),
                    "frequency": oil.get('frequency', ''),
                    "chunk_size": size
                }
            }
            chunked_oils.append(chunk)

        print(f"  ✅ Vytvořeno: {len(chunked_oils)} chunků")
        print(f"  📏 Průměrná velikost: {sum(len(c['text']) for c in chunked_oils)//len(chunked_oils)} znaků")

        return chunked_oils

    def _chunk_book(self, paragraphs: List[Dict], book_id: str) -> List[Dict]:
        """
        Knihy - detekce entit + hybridní chunking
        """
        print(f"\n  📖 {book_id.upper()}")
        print(f"  • Zpracovávám {len(paragraphs)} odstavců...")

        # 1. Detekce entit (kapitol, bylin)
        entities = self._detect_entities(paragraphs)
        print(f"  • Detekováno {len(entities)} entit")

        # 2. Chunking podle velikosti entity
        chunked_entities = []
        for entity in entities:
            entity_chunks = self._chunk_entity(entity, book_id)
            chunked_entities.extend(entity_chunks)

        print(f"  ✅ Vytvořeno: {len(chunked_entities)} chunků")

        # Stats
        small = len([c for c in chunked_entities if c['total_parts'] == 1])
        large = len([c for c in chunked_entities if c['total_parts'] > 1])
        print(f"  • Celé entity: {small}")
        print(f"  • Rozdělené entity: {large}")

        return chunked_entities

    def _detect_entities(self, paragraphs: List[Dict]) -> List[Dict]:
        """
        Detekuje entity (kapitoly, bylinky) z odstavců
        """
        entities = []
        current_entity = None

        for para in paragraphs:
            text = para['text']

            # Je to nadpis?
            if self._is_heading(text):
                # Uložit předchozí entitu
                if current_entity:
                    entities.append(current_entity)

                # Začít novou entitu
                current_entity = {
                    "name": text.strip(),
                    "paragraphs": [],
                    "source_id": para['id']
                }
            else:
                # Přidat k aktuální entitě
                if current_entity:
                    current_entity["paragraphs"].append(para)
                else:
                    # Odstavec bez nadpisu - vytvořit vlastní entitu
                    entities.append({
                        "name": f"Odstavec {para['id']}",
                        "paragraphs": [para],
                        "source_id": para['id']
                    })

        # Uložit poslední entitu
        if current_entity:
            entities.append(current_entity)

        return entities

    def _is_heading(self, text: str) -> bool:
        """
        Detekuje, zda je text nadpis
        """
        # Krátký text (<100 znaků)
        if len(text) > self.config['heading_detection']['max_length']:
            return False

        # Obsahuje klíčová slova
        keywords = self.config['heading_detection']['keywords']
        for keyword in keywords:
            if keyword.lower() in text.lower():
                return True

        # Začíná velkým písmenem + obsahuje číslo
        if text[0].isupper() and any(char.isdigit() for char in text):
            return True

        # Celé uppercase (např. "PÚPAVA LEKÁRSKA")
        if text.isupper() and len(text.split()) <= 5:
            return True

        return False

    def _chunk_entity(self, entity: Dict, book_id: str) -> List[Dict]:
        """
        Chunking jedné entity podle velikosti
        """
        # Spojit odstavce do souvislého textu
        full_text = "\n\n".join([p['text'] for p in entity['paragraphs']])
        entity_size = len(full_text)

        # Rozhodnutí podle velikosti
        small_max = self.config['entity_based']['small_entity_max']
        medium_max = self.config['entity_based']['medium_entity_max']

        if entity_size <= small_max:
            # MALÁ ENTITA - ponechat celou
            return self._create_single_chunk(entity, full_text, book_id)

        elif entity_size <= medium_max:
            # STŘEDNÍ ENTITA - ponechat celou (na hranici)
            return self._create_single_chunk(entity, full_text, book_id)

        else:
            # VELKÁ ENTITA - rozdělit fixed-size
            return self._create_fixed_size_chunks(entity, full_text, book_id)

    def _create_single_chunk(self, entity: Dict, text: str, book_id: str) -> List[Dict]:
        """Vytvoří jeden chunk z celé entity"""
        chunk = {
            "id": f"{book_id}_{entity['source_id']}_full",
            "type": "herb_knowledge",
            "entity_name": entity['name'],
            "entity_type": "herb",
            "text": f"{entity['name']}\n\n{text}",
            "part": 1,
            "total_parts": 1,
            "tier": "premium",  # Default - upravíš podle potřeby
            "metadata": {
                "source": book_id,
                "category": "bylinky",
                "chunk_size": len(text)
            }
        }
        return [chunk]

    def _create_fixed_size_chunks(self, entity: Dict, text: str, book_id: str) -> List[Dict]:
        """Vytvoří fixed-size chunky z velké entity"""
        chunk_size = self.config['fixed_size']['chunk_size']
        overlap = self.config['fixed_size']['overlap']

        chunks = []
        start = 0
        part = 1

        # Přidat název entity na začátek prvního chunku
        text_with_header = f"{entity['name']}\n\n{text}"

        while start < len(text_with_header):
            end = start + chunk_size
            chunk_text = text_with_header[start:end]

            # Vytvořit chunk
            chunk = {
                "id": f"{book_id}_{entity['source_id']}_part_{part}",
                "type": "herb_knowledge",
                "entity_name": entity['name'],
                "entity_type": "herb",
                "text": chunk_text,
                "part": part,
                "total_parts": 0,  # Vypočítáme později
                "tier": "premium",
                "metadata": {
                    "source": book_id,
                    "category": "bylinky",
                    "chunk_size": len(chunk_text)
                }
            }
            chunks.append(chunk)

            start += (chunk_size - overlap)
            part += 1

        # Update total_parts
        total = len(chunks)
        for chunk in chunks:
            chunk['total_parts'] = total

        return chunks

    def _chunk_voice_transcripts(self, transcripts: List[Dict]) -> List[Dict]:
        """
        Voice transkripty - spojit věty + fixed-size chunking
        """
        print(f"  • Zpracovávám {len(transcripts)} vět...")

        # Spojit všechny věty do souvislého textu
        full_text = " ".join([t['text'] for t in transcripts])

        print(f"  • Celková délka: {len(full_text)} znaků")

        # Fixed-size chunking
        chunk_size = self.config['fixed_size']['chunk_size']
        overlap = self.config['fixed_size']['overlap']

        chunks = []
        start = 0
        part = 1

        while start < len(full_text):
            end = start + chunk_size
            chunk_text = full_text[start:end]

            chunk = {
                "id": f"voice_transcript_drienka_part_{part}",
                "type": "herb_knowledge",
                "entity_name": "Drienka obyčajná",  # Z názvu transkriptu
                "entity_type": "herb",
                "text": chunk_text,
                "part": part,
                "total_parts": 0,  # Vypočítáme později
                "tier": "premium",
                "metadata": {
                    "source": "voice_transcript",
                    "category": "bylinky",
                    "duration_minutes": 7.5,  # Z JSON
                    "chunk_size": len(chunk_text)
                }
            }
            chunks.append(chunk)

            start += (chunk_size - overlap)
            part += 1

        # Update total_parts
        total = len(chunks)
        for chunk in chunks:
            chunk['total_parts'] = total

        print(f"  ✅ Vytvořeno: {len(chunks)} chunků")
        print(f"  📏 Průměrná velikost: {sum(len(c['text']) for c in chunks)//len(chunks)} znaků")

        return chunks


def main():
    """Main function"""
    base_path = Path("/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline")

    # Paths
    parsed_data_path = base_path / "parsed_data.json"
    output_path = base_path / "chunked_data.json"

    # Initialize chunking strategy
    chunker = ChunkingStrategy()

    # Apply chunking
    chunked_data = chunker.chunk_all_data(str(parsed_data_path))

    # Save results
    print("\n" + "="*70)
    print("💾 UKLÁDÁM VÝSLEDKY")
    print("="*70)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunked_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Uloženo do: {output_path}")
    print(f"\n📊 FINÁLNÍ STATISTIKY:")
    print(f"  • Esenciální oleje: {chunked_data['stats']['essential_oils']} chunků")
    print(f"  • Knihy o bylinkách: {chunked_data['stats']['herbs_books']} chunků")
    print(f"  • Voice transkripty: {chunked_data['stats']['voice_transcripts']} chunků")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  • CELKEM: {chunked_data['stats']['total']} chunků")

    print("\n" + "="*70)
    print("✅ CHUNKING DOKONČEN!")
    print("="*70)
    print("\n🎯 Další krok: Vytvoření embeddings (sentence-transformers)")


if __name__ == "__main__":
    main()
