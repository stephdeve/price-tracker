"""
Aggregator: groups products (existing rows) into cross-source comparable clusters
using lightweight matching. Additive, no DB schema change.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Dict, Any, Optional

from app.services.matching import score_pair
from app.services.normalization import normalize_title, guess_brand, extract_attributes


@dataclass
class AggregatedOffer:
    product_id: str
    title: str
    marketplace: str
    price: float
    currency: str
    is_available: bool
    url: str
    image_url: Optional[str] = None


@dataclass
class AggregatedGroup:
    canonical_title: str
    brand: Optional[str]
    attributes: Dict[str, Any]
    offers: List[AggregatedOffer] = field(default_factory=list)

    @property
    def best_price(self) -> Optional[float]:
        if not self.offers:
            return None
        return min(o.price for o in self.offers if o.price is not None)

    @property
    def min_price(self) -> Optional[float]:
        return self.best_price

    @property
    def max_price(self) -> Optional[float]:
        if not self.offers:
            return None
        return max(o.price for o in self.offers if o.price is not None)


def group_products(products: Iterable[Any], score_threshold: float = 0.68) -> List[AggregatedGroup]:
    groups: List[AggregatedGroup] = []

    for p in products:
        title = getattr(p, "name", None) or getattr(p, "title", "")
        price = float(getattr(p, "current_price", 0.0) or 0.0)
        currency = getattr(p, "currency", "XOF")
        marketplace = getattr(p, "marketplace", "unknown")
        url = getattr(p, "url", "")
        image_url = getattr(p, "image_url", None)
        pid = getattr(p, "id", None)

        placed = False
        for g in groups:
            if not g.offers:
                continue
            # compare to the first offer as representative
            rep = g.offers[0]
            s, _ = score_pair(title, price, rep.title, rep.price)
            if s >= score_threshold:
                g.offers.append(
                    AggregatedOffer(
                        product_id=pid,
                        title=title,
                        marketplace=str(marketplace),
                        price=price,
                        currency=currency,
                        is_available=bool(getattr(p, "is_available", True)),
                        url=url,
                        image_url=image_url,
                    )
                )
                placed = True
                break
        if placed:
            continue

        # new group
        norm_title = normalize_title(title)
        group = AggregatedGroup(
            canonical_title=norm_title,
            brand=guess_brand(title),
            attributes=extract_attributes(title),
            offers=[
                AggregatedOffer(
                    product_id=pid,
                    title=title,
                    marketplace=str(marketplace),
                    price=price,
                    currency=currency,
                    is_available=bool(getattr(p, "is_available", True)),
                    url=url,
                    image_url=image_url,
                )
            ],
        )
        groups.append(group)

    # sort offers in each group by price asc
    for g in groups:
        g.offers.sort(key=lambda o: (o.price if o.price is not None else 1e18))

    # sort groups by best price asc then by number of offers desc
    groups.sort(key=lambda gr: (gr.best_price if gr.best_price is not None else 1e18, -len(gr.offers)))
    return groups
