CREATE TABLE "category" (
    "category_id" SERIAL PRIMARY KEY,
    "category_title" varchar(50),
    "category_created" timestamp NOT NULL DEFAULT now(),
    "category_updated" timestamp DEFAULT NULL
);

CREATE TABLE "article" (
    "article_id" SERIAL PRIMARY KEY,
    "article_text" text,
    "article_title" varchar(50),
    "article_created" timestamp NOT NULL DEFAULT now(),
    "article_updated" timestamp DEFAULT NULL
);

CREATE TABLE "tag" (
    "tag_id" SERIAL PRIMARY KEY,
    "tag_value" varchar(50),
    "tag_created" timestamp NOT NULL DEFAULT now(),
    "tag_updated" timestamp DEFAULT NULL
);

CREATE TABLE "article__tag" (
    "article_id" INTEGER NOT NULL,
    "tag_id" INTEGER NOT NULL,
    "article__tag_quantity" INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY ("article_id", "tag_id")
);

ALTER TABLE "article__tag"
    ADD CONSTRAINT "fk_article__tag_article_id"
    FOREIGN KEY ("article_id") REFERENCES "article" ("article_id");

ALTER TABLE "article__tag"
    ADD CONSTRAINT "fk_article__tag_tag_id"
    FOREIGN KEY ("tag_id") REFERENCES "tag" ("tag_id");

ALTER TABLE "article" ADD "category_id" INTEGER NOT NULL,
    ADD CONSTRAINT "fk_article_category_id" FOREIGN KEY ("category_id")
    REFERENCES "category" ("category_id");

CREATE OR REPLACE FUNCTION update_category_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.category_updated = now();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE FUNCTION update_article_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.article_updated = now();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE FUNCTION update_tag_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.tag_updated = now();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER "tr_category_updated" BEFORE UPDATE
ON "category" FOR EACH ROW EXECUTE PROCEDURE update_category_timestamp();

CREATE TRIGGER "tr_article_updated" BEFORE UPDATE
ON "article" FOR EACH ROW EXECUTE PROCEDURE update_article_timestamp();

CREATE TRIGGER "tr_tag_updated" BEFORE UPDATE
ON "tag" FOR EACH ROW EXECUTE PROCEDURE update_tag_timestamp();

