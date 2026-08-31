from voynichlab.folds import folio_fold, is_holdout, is_development, HOLDOUT_FOLDS, DEVELOPMENT_FOLDS


def test_fold_deterministic_and_in_range():
    for f in ["f1r", "f78r", "f116v", "F78R"]:
        assert 0 <= folio_fold(f) < 5
    # case-insensitive
    assert folio_fold("f78r") == folio_fold("F78R")


def test_partition_is_disjoint_and_complete():
    assert set(HOLDOUT_FOLDS) | set(DEVELOPMENT_FOLDS) == {0, 1, 2, 3, 4}
    assert set(HOLDOUT_FOLDS) & set(DEVELOPMENT_FOLDS) == set()
    for f in ["f1r", "f78r", "f116v"]:
        assert is_holdout(f) != is_development(f)
