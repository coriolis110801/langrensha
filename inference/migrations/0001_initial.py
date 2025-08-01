# Generated by Django 4.2.23 on 2025-07-26 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number", models.IntegerField(unique=True, verbose_name="玩家编号")),
                (
                    "nickname",
                    models.CharField(blank=True, max_length=50, verbose_name="昵称"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "玩家", "verbose_name_plural": "玩家",},
        ),
        migrations.CreateModel(
            name="WerewolfProbabilityAdjustment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "probability_increase",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="增加概率(%)"
                    ),
                ),
                ("reason", models.TextField(verbose_name="调整原因")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inference.player",
                        verbose_name="目标玩家",
                    ),
                ),
            ],
            options={
                "verbose_name": "匪徒概率调整",
                "verbose_name_plural": "匪徒概率调整",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PoliceIdentity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "police_a",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="police_a_identity",
                        to="inference.player",
                        verbose_name="警察A",
                    ),
                ),
                (
                    "police_b",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="police_b_identity",
                        to="inference.player",
                        verbose_name="警察B",
                    ),
                ),
            ],
            options={"verbose_name": "警察身份", "verbose_name_plural": "警察身份",},
        ),
        migrations.CreateModel(
            name="NightCheck",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "checker",
                    models.CharField(
                        choices=[("A", "警察A"), ("B", "警察B")],
                        max_length=1,
                        verbose_name="查验者",
                    ),
                ),
                (
                    "result",
                    models.CharField(
                        choices=[("good", "好人"), ("bad", "匪徒")],
                        max_length=4,
                        verbose_name="查验结果",
                    ),
                ),
                ("night_number", models.IntegerField(default=1, verbose_name="第几夜")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inference.player",
                        verbose_name="被查验者",
                    ),
                ),
            ],
            options={
                "verbose_name": "夜晚查验",
                "verbose_name_plural": "夜晚查验",
                "ordering": ["night_number", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="Judgment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        choices=[("good", "好人"), ("bad", "匪徒")],
                        max_length=4,
                        verbose_name="判断",
                    ),
                ),
                ("reason", models.TextField(blank=True, verbose_name="判断理由")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inference.player",
                        verbose_name="玩家",
                    ),
                ),
            ],
            options={
                "verbose_name": "主观判断",
                "verbose_name_plural": "主观判断",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="DeathEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[("kill", "夜晚被杀"), ("vote", "白天处决")],
                        max_length=4,
                        verbose_name="事件类型",
                    ),
                ),
                ("night_number", models.IntegerField(default=1, verbose_name="第几夜/天")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inference.player",
                        verbose_name="死亡玩家",
                    ),
                ),
            ],
            options={
                "verbose_name": "死亡事件",
                "verbose_name_plural": "死亡事件",
                "ordering": ["night_number", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="OppositionGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reason", models.TextField(verbose_name="对立原因")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "player_a",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opposition_as_a",
                        to="inference.player",
                        verbose_name="玩家A",
                    ),
                ),
                (
                    "player_b",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opposition_as_b",
                        to="inference.player",
                        verbose_name="玩家B",
                    ),
                ),
            ],
            options={
                "verbose_name": "对立组合",
                "verbose_name_plural": "对立组合",
                "ordering": ["-created_at"],
                "unique_together": {("player_a", "player_b")},
            },
        ),
    ]
