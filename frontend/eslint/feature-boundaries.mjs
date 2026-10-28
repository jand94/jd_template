import path from "node:path";

const rootImport = /^(index)(\.(tsx?|jsx?|mts|cts))?$/;

function slash(value) {
  return value.replaceAll("\\", "/");
}

function srcRootOf(filename) {
  const file = slash(filename);
  const marker = "/src/";
  const index = file.lastIndexOf(marker);
  if (index === -1) {
    return null;
  }
  return file.slice(0, index + marker.length - 1);
}

function zoneOf(filename) {
  const file = slash(filename);
  const srcRoot = srcRootOf(filename);
  if (!srcRoot) {
    return { kind: "outside" };
  }
  const relative = file.slice(srcRoot.length + 1);
  if (relative.startsWith("features/")) {
    const name = relative.slice("features/".length).split("/")[0];
    return name ? { kind: "feature", name } : { kind: "other" };
  }
  if (relative.startsWith("components/") || relative.startsWith("lib/") || relative.startsWith("config/")) {
    return { kind: "shell" };
  }
  if (relative.startsWith("app/")) {
    return { kind: "app" };
  }
  return { kind: "other" };
}

function resolveSpecifier(filename, source) {
  if (source.startsWith("@/")) {
    const srcRoot = srcRootOf(filename);
    if (!srcRoot) {
      return null;
    }
    return path.posix.normalize(`${srcRoot}/${source.slice(2)}`);
  }
  if (source.startsWith(".")) {
    return path.posix.normalize(path.posix.join(path.posix.dirname(slash(filename)), source));
  }
  return null;
}

function targetFeature(abs) {
  const marker = "/src/features/";
  const index = abs.indexOf(marker);
  if (index === -1) {
    return null;
  }
  const parts = abs.slice(index + marker.length).split("/").filter(Boolean);
  const name = parts[0];
  if (!name) {
    return null;
  }
  const rest = parts.slice(1).join("/");
  return { name, root: rest.length === 0 || rootImport.test(rest) };
}

function violation(zone, target) {
  if (!target) {
    return null;
  }
  if (zone.kind === "shell") {
    return "shell";
  }
  if (zone.kind === "feature" && zone.name !== target.name) {
    return "cross";
  }
  if (zone.kind === "app" && !target.root) {
    return "deep";
  }
  return null;
}

function check(context, sourceNode) {
  if (!sourceNode || sourceNode.type !== "Literal" || typeof sourceNode.value !== "string") {
    return;
  }
  const filename = context.filename ?? context.getFilename();
  const resolved = resolveSpecifier(filename, sourceNode.value);
  if (!resolved) {
    return;
  }
  const messageId = violation(zoneOf(filename), targetFeature(resolved));
  if (messageId) {
    context.report({ node: sourceNode, messageId });
  }
}

const rule = {
  meta: {
    type: "problem",
    docs: { description: "Hält die Feature-Grenzen des Templates ein." },
    schema: [],
    messages: {
      shell: "components, lib und config importieren keine Features.",
      cross: "Features importieren keine anderen Features.",
      deep: "Seiten importieren ein Feature nur über @/features/<feature>.",
    },
  },
  create(context) {
    return {
      ImportDeclaration(node) {
        check(context, node.source);
      },
      ImportExpression(node) {
        check(context, node.source);
      },
      ExportNamedDeclaration(node) {
        check(context, node.source);
      },
      ExportAllDeclaration(node) {
        check(context, node.source);
      },
    };
  },
};

const plugin = {
  rules: { boundaries: rule },
};

export default plugin;
