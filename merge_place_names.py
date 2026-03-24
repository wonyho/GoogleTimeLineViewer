#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def parse_latlng(lat_lng_text: str):
    if not isinstance(lat_lng_text, str):
        return None
    parts = lat_lng_text.replace("°", "").split(",")
    if len(parts) != 2:
        return None
    try:
        return float(parts[0].strip()), float(parts[1].strip())
    except ValueError:
        return None


def add_mapping(mapping, obj):
    if not isinstance(obj, dict):
        return
    place_id = obj.get("placeId")
    name = obj.get("name")
    if isinstance(place_id, str) and place_id and isinstance(name, str) and name.strip():
        mapping.setdefault(place_id, name.strip())


def build_place_map_from_timeline_objects(data_json):
    mapping = {}
    for item in data_json.get("timelineObjects", []):
        visit = item.get("placeVisit")
        if isinstance(visit, dict):
            add_mapping(mapping, visit.get("location"))
            for cand in visit.get("otherCandidateLocations", []):
                add_mapping(mapping, cand)

        activity = item.get("activitySegment")
        if isinstance(activity, dict):
            add_mapping(mapping, activity.get("startLocation"))
            add_mapping(mapping, activity.get("endLocation"))
    return mapping


def collect_source_files(single_source: str, source_dir: str):
    files = []
    source_path = Path(single_source)
    if source_path.exists():
        files.append(source_path)

    if source_dir:
        base = Path(source_dir)
        if base.exists():
            for p in sorted(base.rglob("*.json")):
                files.append(p)

    unique = []
    seen = set()
    for f in files:
        key = str(f.resolve())
        if key not in seen:
            unique.append(f)
            seen.add(key)
    return unique


def merge_names_and_build_places(timeline_json, place_map):
    updated = 0
    places_by_coord = {}

    for seg in timeline_json.get("semanticSegments", []):
        visit = seg.get("visit")
        if not isinstance(visit, dict):
            continue
        top = visit.get("topCandidate")
        if not isinstance(top, dict):
            continue

        place_id = top.get("placeId")
        if isinstance(place_id, str) and place_id and not top.get("name"):
            mapped_name = place_map.get(place_id)
            if mapped_name:
                top["name"] = mapped_name
                updated += 1

        place_location = top.get("placeLocation")
        if not isinstance(place_location, dict):
            continue
        lat_lng = parse_latlng(place_location.get("latLng"))
        if not lat_lng:
            continue

        name = top.get("name") or (place_map.get(place_id) if isinstance(place_id, str) else None)
        if not name:
            continue

        lat, lng = lat_lng
        key = (round(lat, 4), round(lng, 4))
        existing = places_by_coord.get(key)
        candidate = {
            "lat": lat,
            "lng": lng,
            "name": name,
        }
        if isinstance(place_id, str) and place_id:
            candidate["placeId"] = place_id

        if not existing:
            places_by_coord[key] = candidate
            continue

        if "placeId" not in existing and "placeId" in candidate:
            existing["placeId"] = candidate["placeId"]
        if (not existing.get("name")) and candidate.get("name"):
            existing["name"] = candidate["name"]

    places = sorted(
        places_by_coord.values(),
        key=lambda x: (x.get("name", ""), x["lat"], x["lng"]),
    )
    return updated, places


def main():
    parser = argparse.ArgumentParser(
        description="Fill visit names using placeId mappings and generate places.json for TimeLineViewer."
    )
    parser.add_argument("--source", default="data.json", help="Primary source JSON (timelineObjects format)")
    parser.add_argument(
        "--source-dir",
        default="Location History (Timeline)/data",
        help="Directory containing monthly timelineObjects JSON files",
    )
    parser.add_argument(
        "--timeline",
        default="TimeLine20260321.json",
        help="Target semantic timeline JSON path",
    )
    parser.add_argument(
        "--output-timeline",
        default="TimeLine20260321.enriched.json",
        help="Output path for enriched semantic timeline JSON",
    )
    parser.add_argument(
        "--output-places",
        default="places.json",
        help="Output path for generated places DB JSON",
    )
    args = parser.parse_args()

    source_files = collect_source_files(args.source, args.source_dir)
    place_map = {}
    loaded_sources = 0
    for src in source_files:
        try:
            src_json = load_json(src)
        except Exception:
            continue
        partial_map = build_place_map_from_timeline_objects(src_json)
        if not partial_map:
            continue
        loaded_sources += 1
        for k, v in partial_map.items():
            place_map.setdefault(k, v)

    timeline_path = Path(args.timeline)
    timeline_json = load_json(timeline_path)
    updated_count, places = merge_names_and_build_places(timeline_json, place_map)

    save_json(Path(args.output_timeline), timeline_json)
    save_json(Path(args.output_places), places)

    print(f"Source files scanned: {len(source_files)}")
    print(f"Source files used: {loaded_sources}")
    print(f"Place map entries: {len(place_map)}")
    print(f"Updated visits: {updated_count}")
    print(f"Generated places: {len(places)}")
    print(f"Wrote timeline: {args.output_timeline}")
    print(f"Wrote places: {args.output_places}")


if __name__ == "__main__":
    main()
