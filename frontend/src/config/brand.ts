function configured(value: string | undefined, fallback: string): string {
  const trimmed = value?.trim();
  return trimmed ? trimmed : fallback;
}

const projectName = configured(process.env.PROJECT_NAME, "jd_Template");

export const brand = {
  projectName,
  apiTitle: configured(process.env.API_TITLE, `${projectName} API`),
  apiDescription: configured(
    process.env.API_DESCRIPTION,
    `HTTP-API für ${projectName}`,
  ),
  apiVersion: configured(process.env.API_VERSION, "0.1.0"),
};
