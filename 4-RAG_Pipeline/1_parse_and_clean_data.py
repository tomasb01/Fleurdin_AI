"""
FLEURDIN AI - DATA PARSING & CLEANING
======================================
Tento script načte všechny zdrojové soubory a vyčistí je do strukturované podoby.

Zdroje:
1. Esenciální oleje (Excel)
2. Bylinky - Kniha 1 (Word)
3. Bylinky - Kniha 2 (Word)
4. Bylinky - Transkript (JSON)

Output: Vyčištěná data ve formátu JSON připravená pro chunking a embeddings
"""

import pandas as pd
import json
from docx import Document
from pathlib import Path
from typing import List, Dict
import re


class DataParser:
    """Parser pro všechny zdrojové soubory"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.parsed_data = {
            "essential_oils": [],
            "herbs_book1": [],
            "herbs_book2": [],
            "herbs_transcript": []
        }

    def parse_essential_oils(self, excel_path: str) -> List[Dict]:
        """
        Parsuje Excel s esenciálními oleji

        VERZE B: Vyčištěná s bullets pro strukturu
        """
        print("\n" + "="*70)
        print("📦 PARSING: Esenciální oleje (Excel)")
        print("="*70)

        df = pd.read_excel(excel_path)
        oils = []

        # Skip header rows (first 2 rows)
        for idx, row in df.iterrows():
            if idx < 2:  # Skip header
                continue

            # Extract data
            oil_id = row.iloc[0]
            name = row.iloc[1]
            english_name = row.iloc[2]
            latin_name = row.iloc[3]
            frequency = row.iloc[4]
            body_effects = str(row.iloc[5]) if pd.notna(row.iloc[5]) else ""
            psyche_effects = str(row.iloc[6]) if pd.notna(row.iloc[6]) else ""

            # Skip if no name
            if pd.isna(name) or name == "":
                continue

            # Clean and format with bullets (VERZE B)
            cleaned_body = self._format_with_bullets(body_effects)
            cleaned_psyche = self._format_with_bullets(psyche_effects)

            # Create structured chunk (1 olej = 1 chunk)
            oil_chunk = f"""OLEJ: {name}

ÚČINKY NA TĚLO:
{cleaned_body}

ÚČINKY NA PSYCHIKU:
{cleaned_psyche}"""

            oil_data = {
                "id": f"oil_{int(oil_id) if pd.notna(oil_id) else idx}",
                "type": "essential_oil",
                "name": name,
                "english_name": english_name if pd.notna(english_name) else "",
                "latin_name": latin_name if pd.notna(latin_name) else "",
                "frequency": frequency if pd.notna(frequency) else "",
                "text": oil_chunk,
                "metadata": {
                    "source": "excel",
                    "category": "esenciální oleje"
                }
            }

            oils.append(oil_data)
            print(f"✅ Parsed: {name}")

        print(f"\n📊 Total oils parsed: {len(oils)}")
        return oils

    def _format_with_bullets(self, text: str) -> str:
        """
        Formátuje text s bullets pro lepší čitelnost

        VERZE B: Přidává • před každou kategorii
        """
        if not text or text == "nan":
            return ""

        # Split by \n\n (major sections)
        sections = text.split("\n\n")
        formatted_sections = []

        for section in sections:
            if section.strip():
                # Split by \n (subsections)
                lines = section.split("\n")
                formatted_lines = []

                for line in lines:
                    if line.strip():
                        # Add bullet
                        formatted_lines.append(f"   • {line.strip()}")

                formatted_sections.append("\n".join(formatted_lines))

        return "\n\n".join(formatted_sections)

    def parse_transcript(self, json_path: str) -> List[Dict]:
        """
        Parsuje JSON transkript z voice-to-text

        VERZE B: Pouze čistý text, bez metadat
        """
        print("\n" + "="*70)
        print("📦 PARSING: Transkript (JSON)")
        print("="*70)

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        sentences = data.get('sentences', [])

        # Extract only text (VERZE B - bez metadat)
        cleaned_sentences = []
        for i, sent in enumerate(sentences):
            text = sent.get('text', '').strip()
            if text:
                cleaned_sentences.append({
                    "id": f"transcript_{i+1}",
                    "type": "transcript",
                    "name": f"Transkript - věta {i+1}",
                    "text": text,
                    "metadata": {
                        "source": "voice_transcript",
                        "category": "bylinky",
                        "sentence_number": i+1
                    }
                })

        print(f"✅ Parsed {len(cleaned_sentences)} sentences")
        print(f"📏 Total length: {sum(len(s['text']) for s in cleaned_sentences)} znaků")

        return cleaned_sentences

    def parse_word_doc(self, doc_path: str, doc_id: str) -> List[Dict]:
        """
        Parsuje Word dokument s bylinkami

        VERZE B: Vyčištěný text po odstavcích
        """
        print("\n" + "="*70)
        print(f"📦 PARSING: {Path(doc_path).name}")
        print("="*70)

        doc = Document(doc_path)

        # Extract non-empty paragraphs
        paragraphs = []
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if text and len(text) > 20:  # Skip very short paragraphs
                paragraphs.append({
                    "id": f"{doc_id}_para_{i+1}",
                    "type": "herb_book",
                    "name": f"{doc_id} - odstavec {i+1}",
                    "text": text,
                    "metadata": {
                        "source": doc_path,
                        "category": "bylinky",
                        "paragraph_number": i+1
                    }
                })

        print(f"✅ Parsed {len(paragraphs)} paragraphs")
        print(f"📏 Total length: {sum(len(p['text']) for p in paragraphs)} znaků")

        return paragraphs

    def parse_all(self):
        """Parsuje všechny zdroje"""
        print("\n" + "="*70)
        print("🚀 ZAČÍNÁM PARSING VŠECH ZDROJŮ")
        print("="*70)

        # 1. Esenciální oleje
        oils_path = self.base_path / "Raw_data/Fleurdin/EO_prehled oleju_30oils_updated.csv.xlsx"
        self.parsed_data["essential_oils"] = self.parse_essential_oils(str(oils_path))

        # 2. Transkript
        transcript_path = self.base_path / "2-EO_Dataset/Voice_recordings/sentences.json"
        self.parsed_data["herbs_transcript"] = self.parse_transcript(str(transcript_path))

        # 3. Kniha 1
        book1_path = self.base_path / "Raw_data/Bylinky_DivokaStrava/Data/Liečivá sila divokých byliniek_po RU_1.2.2023.docx"
        self.parsed_data["herbs_book1"] = self.parse_word_doc(str(book1_path), "book1")

        # 4. Kniha 2
        book2_path = self.base_path / "Raw_data/Bylinky_DivokaStrava/Data/kniha2_hlavny text_rkp_NP_uprava 22-1-25.docx"
        self.parsed_data["herbs_book2"] = self.parse_word_doc(str(book2_path), "book2")

        return self.parsed_data

    def save_parsed_data(self, output_path: str):
        """Uloží parsovaná data do JSON"""
        print("\n" + "="*70)
        print("💾 UKLÁDÁM PARSOVANÁ DATA")
        print("="*70)

        # Combine all data
        all_chunks = (
            self.parsed_data["essential_oils"] +
            self.parsed_data["herbs_transcript"] +
            self.parsed_data["herbs_book1"] +
            self.parsed_data["herbs_book2"]
        )

        output = {
            "total_chunks": len(all_chunks),
            "chunks": all_chunks,
            "stats": {
                "essential_oils": len(self.parsed_data["essential_oils"]),
                "herbs_transcript": len(self.parsed_data["herbs_transcript"]),
                "herbs_book1": len(self.parsed_data["herbs_book1"]),
                "herbs_book2": len(self.parsed_data["herbs_book2"])
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"✅ Uloženo do: {output_path}")
        print(f"📊 Celkový počet chunků: {len(all_chunks)}")
        print("\nStatistiky:")
        for key, value in output["stats"].items():
            print(f"   • {key}: {value} chunků")


def main():
    """Main function"""
    base_path = "/Users/atlas/Projects/Fleurdin_AI"
    output_path = "/Users/atlas/Projects/Fleurdin_AI/4-RAG_Pipeline/parsed_data.json"

    # Parse all data
    parser = DataParser(base_path)
    parser.parse_all()

    # Save to JSON
    parser.save_parsed_data(output_path)

    print("\n" + "="*70)
    print("✅ PARSING DOKONČEN!")
    print("="*70)
    print(f"\nVýstup: {output_path}")
    print("\n🎯 Další krok: Chunking strategie")


if __name__ == "__main__":
    main()
