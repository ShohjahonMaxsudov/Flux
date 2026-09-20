from dataclasses import dataclass


@dataclass
class Note:

    id: int

    title: str = ""

    body: str = ""

    tags: str = ""

    locked: bool = False

    created_at: str = ""

    updated_at: str = ""


    @classmethod
    def from_row(cls, row):

        keys = row.keys()

        def get(name, default=None):
            return row[name] if name in keys else default

        return cls(
            id=get("id"),
            title=get("title") or "",
            body=get("body") or "",
            tags=get("tags") or "",
            locked=bool(get("locked") or 0),
            created_at=get("created_at") or "",
            updated_at=get("updated_at") or ""
        )


    @property
    def preview(self):

        text = " ".join(self.body.split())

        return text[:90] + ("…" if len(text) > 90 else "")


    @property
    def tag_list(self):

        return [t.strip() for t in self.tags.split(",") if t.strip()]
