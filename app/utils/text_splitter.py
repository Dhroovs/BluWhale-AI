from typing import List

class RecursiveCharacterTextSplitter:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, separators: List[str] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        return self._split_text(text, self.separators)

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]

        separator = separators[-1] if separators else ""
        for s in separators:
            if s == "":
                separator = s
                break
            if s in text:
                separator = s
                break

        if separator != "":
            splits = text.split(separator)
        else:
            splits = list(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_len = len(split) + len(separator)
            
            if split_len > self.chunk_size:
                if current_chunk:
                    chunks.append(separator.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                sub_separators = [s for s in separators if s != separator]
                sub_chunks = self._split_text(split, sub_separators)
                chunks.extend(sub_chunks)
            else:
                if current_length + split_len > self.chunk_size:
                    if current_chunk:
                        chunks.append(separator.join(current_chunk))
                    
                    overlap_chunk = []
                    overlap_len = 0
                    for item in reversed(current_chunk):
                        item_len = len(item) + len(separator)
                        if overlap_len + item_len <= self.chunk_overlap:
                            overlap_chunk.insert(0, item)
                            overlap_len += item_len
                        else:
                            break
                    current_chunk = overlap_chunk
                    current_length = overlap_len

                current_chunk.append(split)
                current_length += split_len

        if current_chunk:
            chunks.append(separator.join(current_chunk))

        return [c.strip() for c in chunks if c.strip()]

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)
