from pathlib import Path
import tempfile
import time
from agentlab.experiments import reproducibility_util
from agentlab.agents.generic_agent import AGENT_4o_MINI
import pytest
import json


def test_set_temp():
    agent_args = reproducibility_util.set_temp(AGENT_4o_MINI)
    assert agent_args.chat_model_args.temperature == 0


@pytest.mark.parametrize(
    "benchmark_name",
    ["miniwob", "workarena.l1", "webarena", "visualwebarena"],
)
def test_get_reproducibility_info(benchmark_name):
    info = reproducibility_util.get_reproducibility_info(
        "test_agent", benchmark_name, ignore_changes=True
    )

    print("reproducibility info:")
    print(json.dumps(info, indent=4))

    # assert keys in info
    assert "git_user" in info
    assert "benchmark" in info
    assert "benchmark_version" in info
    assert "agentlab_version" in info
    assert "agentlab_git_hash" in info
    assert "agentlab__local_modifications" in info
    assert "browsergym_version" in info
    assert "browsergym_git_hash" in info
    assert "browsergym__local_modifications" in info


def test_save_reproducibility_info():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        info1 = reproducibility_util.save_reproducibility_info(
            study_dir=tmp_dir,
            info=reproducibility_util.get_reproducibility_info(
                agent_name="test_agent",
                benchmark_name="miniwob",
                ignore_changes=True,
            ),
        )
        time.sleep(1)  # make sure the date changes by at least 1s

        # this should overwrite the previous info since they are the same beside
        # the date
        info2 = reproducibility_util.save_reproducibility_info(
            study_dir=tmp_dir,
            info=reproducibility_util.get_reproducibility_info(
                agent_name="test_agent",
                benchmark_name="miniwob",
                ignore_changes=True,
            ),
        )

        reproducibility_util._assert_compatible(info1, info2)

        # this should not overwrite info2 as the agent name is different, it
        # should raise an error
        with pytest.raises(ValueError):
            reproducibility_util.save_reproducibility_info(
                study_dir=tmp_dir,
                info=reproducibility_util.get_reproducibility_info(
                    agent_name="test_agent_alt",
                    benchmark_name="miniwob",
                    ignore_changes=True,
                ),
            )

        # load json
        info3 = reproducibility_util.load_reproducibility_info(tmp_dir)

        assert info2 == info3
        assert info1 != info3

        test_study_dir = Path(__file__).parent.parent / "data" / "test_study"

        reproducibility_util.add_reward(info3, test_study_dir, ignore_incomplete=True)
        reproducibility_util.append_to_journal(info3, journal_path=tmp_dir / "journal.csv")
        print((tmp_dir / "journal.csv").read_text())


if __name__ == "__main__":
    # test_set_temp()
    # test_get_reproducibility_info()
    test_save_reproducibility_info()
    pass
