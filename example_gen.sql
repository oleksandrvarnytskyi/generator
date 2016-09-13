INSERT INTO "category" ("category_title") VALUES
('category1'),
('category2'),
('category3');

INSERT INTO "tag" ("tag_value") VALUES
('tag1'),
('tag2'),
('tag3');

INSERT INTO "article" ("article_text", "article_title", "category_id") VALUES
('interesting text', 'title', 1),
('interesting text2', 'title2', 2),
('interesting text2', 'title2', 2),
('interesting text2', 'title3', 3);

INSERT INTO "article__tag" ("article_id", "tag_id", "article__tag_quantity") VALUES
(1, 2, 7),
(3, 2, 5),
(4, 1, 2);
